import inspect
import time

from .UrlEncoded import UrlEncoded
from splunklib.data import Record
from splunklib.exceptions import HTTPError

from .handler import handler
from .utils import _encode, _parse_cookies

# Given an HTTP request handler, this wrapper objects provides a related
# family of convenience methods built using that handler.


class HttpLib:
    """A set of convenient methods for making HTTP calls.

    ``HttpLib`` provides a general :meth:`request` method, and :meth:`delete`,
    :meth:`post`, and :meth:`get` methods for the three HTTP methods that Splunk
    uses.

    By default, ``HttpLib`` uses Python's built-in ``httplib`` library,
    but you can replace it by passing your own handling function to the
    constructor for ``HttpLib``.

    The handling function should have the type:

        ``handler(`url`, `request_dict`) -> response_dict``

    where `url` is the URL to make the request to (including any query and
    fragment sections) as a dictionary with the following keys:

        - method: The method for the request, typically ``GET``, ``POST``, or ``DELETE``.

        - headers: A list of pairs specifying the HTTP headers (for example: ``[('key': value), ...]``).

        - body: A string containing the body to send with the request (this string
          should default to '').

    and ``response_dict`` is a dictionary with the following keys:

        - status: An integer containing the HTTP status code (such as 200 or 404).

        - reason: The reason phrase, if any, returned by the server.

        - headers: A list of pairs containing the response headers (for example, ``[('key': value), ...]``).

        - body: A stream-like object supporting ``read(size=None)`` and ``close()``
          methods to get the body of the response.

    The response dictionary is returned directly by ``HttpLib``'s methods with
    no further processing. By default, ``HttpLib`` calls the :func:`handler` function
    to get a handler function.

    If using the default handler, SSL verification can be disabled by passing verify=False.
    """

    def __init__(self, custom_handler=None, verify=False, key_file=None, cert_file=None, context=None, retries=0,
                 retryDelay=10):
        if custom_handler is None:
            self.handler = handler(verify=verify, key_file=key_file, cert_file=cert_file, context=context)
        else:
            self.handler = custom_handler
        self._cookies = {}
        self.retries = retries
        self.retryDelay = retryDelay

    def delete(self, url, headers=None, **kwargs):
        """Sends a DELETE request to a URL.

        :param url: The URL.
        :type url: ``string``
        :param headers: A list of pairs specifying the headers for the HTTP
            response (for example, ``[('Content-Type': 'text/cthulhu'), ('Token': 'boris')]``).
        :type headers: ``list``
        :param kwargs: Additional keyword arguments (optional). These arguments
            are interpreted as the query part of the URL. The order of keyword
            arguments is not preserved in the request, but the keywords and
            their arguments will be URL encoded.
        :type kwargs: ``dict``
        :returns: A dictionary describing the response (see :class:`HttpLib` for
            its structure).
        :rtype: ``dict``
        """
        if headers is None:
            headers = []
        if kwargs:
            # url is already a UrlEncoded. We have to manually declare
            # the query to be encoded or it will get automatically URL
            # encoded by being appended to url.
            url = url + UrlEncoded('?' + _encode(**kwargs), skip_encode=True)
        message = {
            'method': "DELETE",
            'headers': headers,
        }
        return self.request(url, message)

    def get(self, url, headers=None, **kwargs):
        """Sends a GET request to a URL.

        :param url: The URL.
        :type url: ``string``
        :param headers: A list of pairs specifying the headers for the HTTP
            response (for example, ``[('Content-Type': 'text/cthulhu'), ('Token': 'boris')]``).
        :type headers: ``list``
        :param kwargs: Additional keyword arguments (optional). These arguments
            are interpreted as the query part of the URL. The order of keyword
            arguments is not preserved in the request, but the keywords and
            their arguments will be URL encoded.
        :type kwargs: ``dict``
        :returns: A dictionary describing the response (see :class:`HttpLib` for
            its structure).
        :rtype: ``dict``
        """
        if headers is None:
            headers = []
        if kwargs:
            # url is already a UrlEncoded. We have to manually declare
            # the query to be encoded or it will get automatically URL
            # encoded by being appended to url.
            url = url + UrlEncoded('?' + _encode(**kwargs), skip_encode=True)
        return self.request(url, {'method': "GET", 'headers': headers})

    def post(self, url, headers=None, **kwargs):
        """Sends a POST request to a URL.

        :param url: The URL.
        :type url: ``string``
        :param headers: A list of pairs specifying the headers for the HTTP
            response (for example, ``[('Content-Type': 'text/cthulhu'), ('Token': 'boris')]``).
        :type headers: ``list``
        :param kwargs: Additional keyword arguments (optional). If the argument
            is ``body``, the value is used as the body for the request, and the
            keywords and their arguments will be URL encoded. If there is no
            ``body`` keyword argument, all the keyword arguments are encoded
            into the body of the request in the format ``x-www-form-urlencoded``.
        :type kwargs: ``dict``
        :returns: A dictionary describing the response (see :class:`HttpLib` for
            its structure).
        :rtype: ``dict``
        """
        if headers is None:
            headers = []

        # We handle GET-style arguments and an unstructured body. This is here
        # to support the receivers/stream endpoint.
        if 'body' in kwargs:
            # We only use application/x-www-form-urlencoded if there is no other
            # Content-Type header present. This can happen in cases where we
            # send requests as application/json, e.g. for KV Store.
            if len([x for x in headers if x[0].lower() == "content-type"]) == 0:
                headers.append(("Content-Type", "application/x-www-form-urlencoded"))

            body = kwargs.pop('body')
            if isinstance(body, dict):
                body = _encode(**body).encode('utf-8')
            if len(kwargs) > 0:
                url = url + UrlEncoded('?' + _encode(**kwargs), skip_encode=True)
        else:
            body = _encode(**kwargs).encode('utf-8')
        message = {
            'method': "POST",
            'headers': headers,
            'body': body
        }
        return self.request(url, message)

    def request(self, url, message, **kwargs):
        """Issues an HTTP request to a URL.

        :param url: The URL.
        :type url: ``string``
        :param message: A dictionary with the format as described in
            :class:`HttpLib`.
        :type message: ``dict``
        :param kwargs: Additional keyword arguments (optional). These arguments
            are passed unchanged to the handler.
        :type kwargs: ``dict``
        :returns: A dictionary describing the response (see :class:`HttpLib` for
            its structure).
        :rtype: ``dict``
        """
        while True:
            try:
                response = self.handler(url, message, **kwargs)
                break
            except Exception:
                if self.retries <= 0:
                    raise
                else:
                    time.sleep(self.retryDelay)
                    self.retries -= 1
        response = Record(response)
        if 400 <= response.status:
            raise HTTPError(response)

        # Update the cookie with any HTTP request
        # Initially, assume list of 2-tuples
        key_value_tuples = response.headers
        # If response.headers is a dict, get the key-value pairs as 2-tuples
        # this is the case when using urllib2
        if isinstance(response.headers, dict):
            key_value_tuples = list(response.headers.items())
        for key, value in key_value_tuples:
            if key.lower() == "set-cookie":
                _parse_cookies(value, self._cookies)

        return response
