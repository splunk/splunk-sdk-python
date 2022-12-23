"""The **splunklib.binding** module provides a low-level binding interface to the
`Splunk REST API <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTcontents>`_.

This module handles the wire details of calling the REST API, such as
authentication tokens, prefix paths, URL encoding, and so on. Actual path
segments, ``GET`` and ``POST`` arguments, and the parsing of responses is left
to the user.

If you want a friendlier interface to the Splunk REST API, use the
:mod:`splunklib.client` module.
"""

from .Context import Context
from .ResponseReader import ResponseReader
from .UrlEncoded import UrlEncoded
from .NoAuthenticationToken import _NoAuthenticationToken as _NoAuthenticationToken
from .handler import handler


def connect(**kwargs):
    """This function returns an authenticated :class:`Context` object.

    This function is a shorthand for calling :meth:`Context.login`.

    This function makes one round trip to the server.

    :param host: The host name (the default is "localhost").
    :type host: ``string``
    :param port: The port number (the default is 8089).
    :type port: ``integer``
    :param scheme: The scheme for accessing the service (the default is "https").
    :type scheme: "https" or "http"
    :param owner: The owner context of the namespace (the default is "None").
    :type owner: ``string``
    :param app: The app context of the namespace (the default is "None").
    :type app: ``string``
    :param sharing: The sharing mode for the namespace (the default is "user").
    :type sharing: "global", "system", "app", or "user"
    :param token: The current session token (optional). Session tokens can be
        shared across multiple service instances.
    :type token: ``string``
    :param cookie: A session cookie. When provided, you don't need to call :meth:`login`.
        This parameter is only supported for Splunk 6.2+.
    :type cookie: ``string``
    :param username: The Splunk account username, which is used to
        authenticate the Splunk instance.
    :type username: ``string``
    :param password: The password for the Splunk account.
    :type password: ``string``
    :param headers: List of extra HTTP headers to send (optional).
    :type headers: ``list`` of 2-tuples.
    :param autologin: When ``True``, automatically tries to log in again if the
        session terminates.
    :type autologin: ``Boolean``
    :return: An initialized :class:`Context` instance.

    **Example**::

        import splunklib.binding as binding
        c = binding.connect(...)
        response = c.get("apps/local")
    """
    c = Context(**kwargs)
    c.login()
    return c
