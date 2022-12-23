import contextlib
import socket
from datetime import datetime, timedelta
from time import sleep
from urllib import parse

from .Entity import Entity
from splunklib.exceptions import OperationError

from splunklib.binding import _NoAuthenticationToken, UrlEncoded
from splunklib.binding.utils import _make_cookie_header
from splunklib.constants import PATH_RECEIVERS_SIMPLE, PATH_RECEIVERS_STREAM


class Index(Entity):
    """This class represents an index and provides different operations, such as
    cleaning the index, writing to the index, and so forth."""

    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def attach(self, host=None, source=None, sourcetype=None):
        """Opens a stream (a writable socket) for writing events to the index.

        :param host: The host value for events written to the stream.
        :type host: ``string``
        :param source: The source value for events written to the stream.
        :type source: ``string``
        :param sourcetype: The sourcetype value for events written to the
            stream.
        :type sourcetype: ``string``

        :return: A writable socket.
        """
        args = {'index': self.name}
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype
        path = UrlEncoded(PATH_RECEIVERS_STREAM + "?" + parse.urlencode(args), skip_encode=True)

        cookie_header = self.service.token if self.service.token is _NoAuthenticationToken else self.service.token.replace("Splunk ", "")
        cookie_or_auth_header = f"Authorization: Splunk {cookie_header}\r\n"

        # If we have cookie(s), use them instead of "Authorization: ..."
        if self.service.has_cookies():
            cookie_header = _make_cookie_header(list(self.service.get_cookies().items()))
            cookie_or_auth_header = f"Cookie: {cookie_header}\r\n"

        # Since we need to stream to the index connection, we have to keep
        # the connection open and use the Splunk extension headers to note
        # the input mode
        sock = self.service.connect()
        headers = [f"POST {str(self.service._abspath(path))} HTTP/1.1\r\n".encode('utf-8'),
                   f"Host: {self.service.host}:{int(self.service.port)}\r\n".encode('utf-8'),
                   b"Accept-Encoding: identity\r\n",
                   cookie_or_auth_header.encode('utf-8'),
                   b"X-Splunk-Input-Mode: Streaming\r\n",
                   b"\r\n"]

        for h in headers:
            sock.write(h)
        return sock

    @contextlib.contextmanager
    def attached_socket(self, *args, **kwargs):
        """Opens a raw socket in a ``with`` block to write data to Splunk.

        The arguments are identical to those for :meth:`attach`. The socket is
        automatically closed at the end of the ``with`` block, even if an
        exception is raised in the block.

        :param host: The host value for events written to the stream.
        :type host: ``string``
        :param source: The source value for events written to the stream.
        :type source: ``string``
        :param sourcetype: The sourcetype value for events written to the
            stream.
        :type sourcetype: ``string``

        :returns: Nothing.

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            index = s.indexes['some_index']
            with index.attached_socket(sourcetype='test') as sock:
                sock.send('Test event\\r\\n')

        """
        try:
            sock = self.attach(*args, **kwargs)
            yield sock
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def clean(self, timeout=60):
        """Deletes the contents of the index.

        This method blocks until the index is empty, because it needs to restore
        values at the end of the operation.

        :param timeout: The time-out period for the operation, in seconds (the
            default is 60).
        :type timeout: ``integer``

        :return: The :class:`Index`.
        """
        self.refresh()

        tds = self['maxTotalDataSizeMB']
        ftp = self['frozenTimePeriodInSecs']
        was_disabled_initially = self.disabled
        try:
            if not was_disabled_initially and self.service.splunk_version < (5,):
                # Need to disable the index first on Splunk 4.x,
                # but it doesn't work to disable it on 5.0.
                self.disable()
            self.update(maxTotalDataSizeMB=1, frozenTimePeriodInSecs=1)
            self.roll_hot_buckets()

            # Wait until event count goes to 0.
            start = datetime.now()
            diff = timedelta(seconds=timeout)
            while self.content.totalEventCount != '0' and datetime.now() < start + diff:
                sleep(1)
                self.refresh()

            if self.content.totalEventCount != '0':
                raise OperationError(
                    f"Cleaning index {self.name} took longer than {timeout} seconds; timing out.")
        finally:
            # Restore original values
            self.update(maxTotalDataSizeMB=tds, frozenTimePeriodInSecs=ftp)
            if not was_disabled_initially and self.service.splunk_version < (5,):
                # Re-enable the index if it was originally enabled and we messed with it.
                self.enable()

        return self

    def roll_hot_buckets(self):
        """Performs rolling hot buckets for this index.

        :return: The :class:`Index`.
        """
        self.post("roll-hot-buckets")
        return self

    def submit(self, event, host=None, source=None, sourcetype=None):
        """Submits a single event to the index using ``HTTP POST``.

        :param event: The event to submit.
        :type event: ``string``
        :param `host`: The host value of the event.
        :type host: ``string``
        :param `source`: The source value of the event.
        :type source: ``string``
        :param `sourcetype`: The sourcetype value of the event.
        :type sourcetype: ``string``

        :return: The :class:`Index`.
        """
        args = {'index': self.name}
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype

        self.service.post(PATH_RECEIVERS_SIMPLE, body=event, **args)
        return self

    # kwargs: host, host_regex, host_segment, rename-source, sourcetype
    def upload(self, filename, **kwargs):
        """Uploads a file for immediate indexing.

        **Note**: The file must be locally accessible from the server.

        :param filename: The name of the file to upload. The file can be a plain, compressed, or archived file. :type
        filename: ``string`` :param kwargs: Additional arguments (optional). For more about the available parameters,
        see `Index parameters <http://dev.splunk.com/view/SP-CAAAEE6#indexparams>`_ on Splunk Developer Portal. :type
        kwargs: ``dict``

        :return: The :class:`Index`.
        """
        kwargs['index'] = self.name
        path = 'data/inputs/oneshot'
        self.service.post(path, name=filename, **kwargs)
        return self
