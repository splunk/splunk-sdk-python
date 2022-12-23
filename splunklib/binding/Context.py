import logging
import socket
import ssl
from base64 import b64encode
from xml.etree.ElementTree import XML

from .HttpLib import HttpLib
from .UrlEncoded import UrlEncoded
from .NoAuthenticationToken import _NoAuthenticationToken
from .utils import _authority, _encode, _make_cookie_header, namespace, _parse_cookies, _authentication, _log_duration
from splunklib.constants import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SCHEME
from splunklib.exceptions import AuthenticationError, HTTPError

logger = logging.getLogger(__name__)


class Context:
    """This class represents a context that encapsulates a splunkd connection.

    The ``Context`` class encapsulates the details of HTTP requests,
    authentication, a default namespace, and URL prefixes to simplify access to
    the REST API.

    After creating a ``Context`` object, you must call its :meth:`login`
    method before you can issue requests to splunkd. Or, use the :func:`connect`
    function to create an already-authenticated ``Context`` object. You can
    provide a session token explicitly (the same token can be shared by multiple
    ``Context`` objects) to provide authentication.

    :param host: The host name (the default is "localhost").
    :type host: ``string``
    :param port: The port number (the default is 8089).
    :type port: ``integer``
    :param scheme: The scheme for accessing the service (the default is "https").
    :type scheme: "https" or "http"
    :param verify: Enable (True) or disable (False) SSL verification for https connections.
    :type verify: ``Boolean``
    :param sharing: The sharing mode for the namespace (the default is "user").
    :type sharing: "global", "system", "app", or "user"
    :param owner: The owner context of the namespace (optional, the default is "None").
    :type owner: ``string``
    :param app: The app context of the namespace (optional, the default is "None").
    :type app: ``string``
    :param token: A session token. When provided, you don't need to call :meth:`login`.
    :type token: ``string``
    :param cookie: A session cookie. When provided, you don't need to call :meth:`login`.
        This parameter is only supported for Splunk 6.2+.
    :type cookie: ``string``
    :param username: The Splunk account username, which is used to
        authenticate the Splunk instance.
    :type username: ``string``
    :param password: The password for the Splunk account.
    :type password: ``string``
    :param splunkToken: Splunk authentication token
    :type splunkToken: ``string``
    :param headers: List of extra HTTP headers to send (optional).
    :type headers: ``list`` of 2-tuples.
    :param retires: Number of retries for each HTTP connection (optional, the default is 0).
                    NOTE THAT THIS MAY INCREASE THE NUMBER OF ROUND TRIP CONNECTIONS TO THE SPLUNK SERVER AND BLOCK THE
                    CURRENT THREAD WHILE RETRYING.
    :type retries: ``int``
    :param retryDelay: How long to wait between connection attempts if `retries` > 0 (optional, defaults to 10s).
    :type retryDelay: ``int`` (in seconds)
    :param handler: The HTTP request handler (optional).
    :returns: A ``Context`` instance.

    **Example**::

        import splunklib.binding as binding
        c = binding.Context(username="boris", password="natasha", ...)
        c.login()
        # Or equivalently
        c = binding.connect(username="boris", password="natasha")
        # Or if you already have a session token
        c = binding.Context(token="atg232342aa34324a")
        # Or if you already have a valid cookie
        c = binding.Context(cookie="splunkd_8089=...")
    """

    def __init__(self, handler=None, **kwargs):
        self.http = HttpLib(handler, kwargs.get("verify", False), key_file=kwargs.get("key_file"),
                            cert_file=kwargs.get("cert_file"), context=kwargs.get("context"),
                            # Default to False for backward compat
                            retries=kwargs.get("retries", 0), retryDelay=kwargs.get("retryDelay", 10))
        self.token = kwargs.get("token", _NoAuthenticationToken)
        if self.token is None:  # In case someone explicitly passes token=None
            self.token = _NoAuthenticationToken
        self.scheme = kwargs.get("scheme", DEFAULT_SCHEME)
        self.host = kwargs.get("host", DEFAULT_HOST)
        self.port = int(kwargs.get("port", DEFAULT_PORT))
        self.authority = _authority(self.scheme, self.host, self.port)
        self.namespace = namespace(**kwargs)
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        self.basic = kwargs.get("basic", False)
        self.bearerToken = kwargs.get("splunkToken", "")
        self.autologin = kwargs.get("autologin", False)
        self.additional_headers = kwargs.get("headers", [])

        # Store any cookies in the self.http._cookies dict
        if "cookie" in kwargs and kwargs['cookie'] not in [None, _NoAuthenticationToken]:
            _parse_cookies(kwargs["cookie"], self.http._cookies)

    def get_cookies(self):
        """Gets the dictionary of cookies from the ``HttpLib`` member of this instance.

        :return: Dictionary of cookies stored on the ``self.http``.
        :rtype: ``dict``
        """
        return self.http._cookies

    def has_cookies(self):
        """Returns true if the ``HttpLib`` member of this instance has auth token stored.

        :return: ``True`` if there is auth token present, else ``False``
        :rtype: ``bool``
        """
        auth_token_key = "splunkd_"
        return any(auth_token_key in key for key in list(self.get_cookies().keys()))

    # Shared per-context request headers
    @property
    def _auth_headers(self):
        """Headers required to authenticate a request.

        Assumes your ``Context`` already has a authentication token or
        cookie, either provided explicitly or obtained by logging
        into the Splunk instance.

        :returns: A list of 2-tuples containing key and value
        """
        header = []
        if self.has_cookies():
            return [("Cookie", _make_cookie_header(list(self.get_cookies().items())))]
        elif self.basic and (self.username and self.password):
            token = f'Basic {b64encode(("%s:%s" % (self.username, self.password)).encode("utf-8")).decode("ascii")}'
        elif self.bearerToken:
            token = f'Bearer {self.bearerToken}'
        elif self.token is _NoAuthenticationToken:
            token = []
        else:
            # Ensure the token is properly formatted
            if self.token.startswith('Splunk '):
                token = self.token
            else:
                token = f'Splunk {self.token}'
        if token:
            header.append(("Authorization", token))
        if self.get_cookies():
            header.append(("Cookie", _make_cookie_header(list(self.get_cookies().items()))))

        return header

    def connect(self):
        """Returns an open connection (socket) to the Splunk instance.

        This method is used for writing bulk events to an index or similar tasks
        where the overhead of opening a connection multiple times would be
        prohibitive.

        :returns: A socket.

        **Example**::

            import splunklib.binding as binding
            c = binding.connect(...)
            socket = c.connect()
            socket.write("POST %s HTTP/1.1\\r\\n" % "some/path/to/post/to")
            socket.write("Host: %s:%s\\r\\n" % (c.host, c.port))
            socket.write("Accept-Encoding: identity\\r\\n")
            socket.write("Authorization: %s\\r\\n" % c.token)
            socket.write("X-Splunk-Input-Mode: Streaming\\r\\n")
            socket.write("\\r\\n")
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.scheme == "https":
            sock = ssl.wrap_socket(sock)
        sock.connect((socket.gethostbyname(self.host), self.port))
        return sock

    @_authentication
    @_log_duration
    def delete(self, path_segment, owner=None, app=None, sharing=None, **query):
        """Performs a DELETE operation at the REST path segment with the given
        namespace and query.

        This method is named to match the HTTP method. ``delete`` makes at least
        one round trip to the server, one additional round trip for each 303
        status returned, and at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        If *owner*, *app*, and *sharing* are omitted, this method uses the
        default :class:`Context` namespace. All other keyword arguments are
        included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Context`` object is not
             logged in.
        :raises HTTPError: Raised when an error occurred in a GET operation from
             *path_segment*.
        :param path_segment: A REST path segment.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode of the namespace (optional).
        :type sharing: ``string``
        :param query: All other keyword arguments, which are used as query
            parameters.
        :type query: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.delete('saved/searches/boris') == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '1786'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:53:06 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            c.delete('nonexistant/path') # raises HTTPError
            c.logout()
            c.delete('apps/local') # raises AuthenticationError
        """
        path = self.authority + self._abspath(path_segment, owner=owner,
                                              app=app, sharing=sharing)
        logger.debug("DELETE request to %s (body: %s)", path, repr(query))
        response = self.http.delete(path, self._auth_headers, **query)
        return response

    @_authentication
    @_log_duration
    def get(self, path_segment, owner=None, app=None, headers=None, sharing=None, **query):
        """Performs a GET operation from the REST path segment with the given
        namespace and query.

        This method is named to match the HTTP method. ``get`` makes at least
        one round trip to the server, one additional round trip for each 303
        status returned, and at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        If *owner*, *app*, and *sharing* are omitted, this method uses the
        default :class:`Context` namespace. All other keyword arguments are
        included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Context`` object is not
             logged in.
        :raises HTTPError: Raised when an error occurred in a GET operation from
             *path_segment*.
        :param path_segment: A REST path segment.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param headers: List of extra HTTP headers to send (optional).
        :type headers: ``list`` of 2-tuples.
        :param sharing: The sharing mode of the namespace (optional).
        :type sharing: ``string``
        :param query: All other keyword arguments, which are used as query
            parameters.
        :type query: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.get('apps/local') == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '26208'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:30:35 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            c.get('nonexistant/path') # raises HTTPError
            c.logout()
            c.get('apps/local') # raises AuthenticationError
        """
        if headers is None:
            headers = []

        path = self.authority + self._abspath(path_segment, owner=owner,
                                              app=app, sharing=sharing)
        logger.debug("GET request to %s (body: %s)", path, repr(query))
        all_headers = headers + self.additional_headers + self._auth_headers
        response = self.http.get(path, all_headers, **query)
        return response

    @_authentication
    @_log_duration
    def post(self, path_segment, owner=None, app=None, sharing=None, headers=None, **query):
        """Performs a POST operation from the REST path segment with the given
        namespace and query.

        This method is named to match the HTTP method. ``post`` makes at least
        one round trip to the server, one additional round trip for each 303
        status returned, and at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        If *owner*, *app*, and *sharing* are omitted, this method uses the
        default :class:`Context` namespace. All other keyword arguments are
        included in the URL as query parameters.

        Some of Splunk's endpoints, such as ``receivers/simple`` and
        ``receivers/stream``, require unstructured data in the POST body
        and all metadata passed as GET-style arguments. If you provide
        a ``body`` argument to ``post``, it will be used as the POST
        body, and all other keyword arguments will be passed as
        GET-style arguments in the URL.

        :raises AuthenticationError: Raised when the ``Context`` object is not
             logged in.
        :raises HTTPError: Raised when an error occurred in a GET operation from
             *path_segment*.
        :param path_segment: A REST path segment.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode of the namespace (optional).
        :type sharing: ``string``
        :param headers: List of extra HTTP headers to send (optional).
        :type headers: ``list`` of 2-tuples.
        :param query: All other keyword arguments, which are used as query
            parameters.
        :param body: Parameters to be used in the post body. If specified,
            any parameters in the query will be applied to the URL instead of
            the body. If a dict is supplied, the key-value pairs will be form
            encoded. If a string is supplied, the body will be passed through
            in the request unchanged.
        :type body: ``dict`` or ``str``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.post('saved/searches', name='boris',
                   search='search * earliest=-1m | head 1') == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '10455'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:46:06 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'Created',
                 'status': 201}
            c.post('nonexistant/path') # raises HTTPError
            c.logout()
            # raises AuthenticationError:
            c.post('saved/searches', name='boris',
                   search='search * earliest=-1m | head 1')
        """
        if headers is None:
            headers = []

        path = self.authority + self._abspath(path_segment, owner=owner, app=app, sharing=sharing)

        # To avoid writing sensitive data in debug logs
        endpoint_having_sensitive_data = ["/storage/passwords"]
        if any(endpoint in path for endpoint in endpoint_having_sensitive_data):
            logger.debug("POST request to %s ", path)
        else:
            logger.debug("POST request to %s (body: %s)", path, repr(query))
        all_headers = headers + self.additional_headers + self._auth_headers
        response = self.http.post(path, all_headers, **query)
        return response

    @_authentication
    @_log_duration
    def request(self, path_segment, method="GET", headers=None, body={},
                owner=None, app=None, sharing=None):
        """Issues an arbitrary HTTP request to the REST path segment.

        This method is named to match ``httplib.request``. This function
        makes a single round trip to the server.

        If *owner*, *app*, and *sharing* are omitted, this method uses the
        default :class:`Context` namespace. All other keyword arguments are
        included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Context`` object is not
             logged in.
        :raises HTTPError: Raised when an error occurred in a GET operation from
             *path_segment*.
        :param path_segment: A REST path segment.
        :type path_segment: ``string``
        :param method: The HTTP method to use (optional).
        :type method: ``string``
        :param headers: List of extra HTTP headers to send (optional).
        :type headers: ``list`` of 2-tuples.
        :param body: Content of the HTTP request (optional).
        :type body: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode of the namespace (optional).
        :type sharing: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.request('saved/searches', method='GET') == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '46722'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 17:24:19 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            c.request('nonexistant/path', method='GET') # raises HTTPError
            c.logout()
            c.get('apps/local') # raises AuthenticationError
        """
        if headers is None:
            headers = []

        path = self.authority \
               + self._abspath(path_segment, owner=owner,
                               app=app, sharing=sharing)

        all_headers = headers + self.additional_headers + self._auth_headers
        logger.debug("%s request to %s (headers: %s, body: %s)",
                     method, path, str(all_headers), repr(body))

        if body:
            body = _encode(**body)

            if method == "GET":
                path = path + UrlEncoded('?' + body, skip_encode=True)
                message = {'method': method,
                           'headers': all_headers}
            else:
                message = {'method': method,
                           'headers': all_headers,
                           'body': body}
        else:
            message = {'method': method,
                       'headers': all_headers}

        response = self.http.request(path, message)

        return response

    def login(self):
        """Logs into the Splunk instance referred to by the :class:`Context`
        object.

        Unless a ``Context`` is created with an explicit authentication token
        (probably obtained by logging in from a different ``Context`` object)
        you must call :meth:`login` before you can issue requests.
        The authentication token obtained from the server is stored in the
        ``token`` field of the ``Context`` object.

        :raises AuthenticationError: Raised when login fails.
        :returns: The ``Context`` object, so you can chain calls.

        **Example**::

            import splunklib.binding as binding
            c = binding.Context(...).login()
            # Then issue requests...
        """

        if self.has_cookies() and \
                (not self.username and not self.password):
            # If we were passed session cookie(s), but no username or
            # password, then login is a nop, since we're automatically
            # logged in.
            return

        if self.token is not _NoAuthenticationToken and \
                (not self.username and not self.password):
            # If we were passed a session token, but no username or
            # password, then login is a nop, since we're automatically
            # logged in.
            return

        if self.basic and (self.username and self.password):
            # Basic auth mode requested, so this method is a nop as long
            # as credentials were passed in.
            return

        if self.bearerToken:
            # Bearer auth mode requested, so this method is a nop as long
            # as authentication token was passed in.
            return
        # Only try to get a token and updated cookie if username & password are specified
        try:
            response = self.http.post(
                self.authority + self._abspath("/services/auth/login"),
                username=self.username,
                password=self.password,
                headers=self.additional_headers,
                cookie="1")  # In Splunk 6.2+, passing "cookie=1" will return the "set-cookie" header

            body = response.body.read()
            session = XML(body).findtext("./sessionKey")
            self.token = f"Splunk {session}"
            return self
        except HTTPError as he:
            if he.status == 401:
                raise AuthenticationError("Login failed.", he)
            else:
                raise

    def logout(self):
        """Forgets the current session token, and cookies."""
        self.token = _NoAuthenticationToken
        self.http._cookies = {}
        return self

    def _abspath(self, path_segment,
                 owner=None, app=None, sharing=None):
        """Qualifies *path_segment* into an absolute path for a URL.

        If *path_segment* is already absolute, returns it unchanged.
        If *path_segment* is relative, then qualifies it with either
        the provided namespace arguments or the ``Context``'s default
        namespace. Any forbidden characters in *path_segment* are URL
        encoded. This function has no network activity.

        Named to be consistent with RFC2396_.

        .. _RFC2396: http://www.ietf.org/rfc/rfc2396.txt

        :param path_segment: A relative or absolute URL path segment.
        :type path_segment: ``string``
        :param owner, app, sharing: Components of a namespace (defaults
                                    to the ``Context``'s namespace if all
                                    three are omitted)
        :type owner, app, sharing: ``string``
        :return: A ``UrlEncoded`` (a subclass of ``str``).
        :rtype: ``string``

        **Example**::

            import splunklib.binding as binding
            c = binding.connect(owner='boris', app='search', sharing='user')
            c._abspath('/a/b/c') == '/a/b/c'
            c._abspath('/a/b c/d') == '/a/b%20c/d'
            c._abspath('apps/local/search') == \
                '/servicesNS/boris/search/apps/local/search'
            c._abspath('apps/local/search', sharing='system') == \
                '/servicesNS/nobody/system/apps/local/search'
            url = c.authority + c._abspath('apps/local/sharing')
        """
        skip_encode = isinstance(path_segment, UrlEncoded)
        # If path_segment is absolute, escape all forbidden characters
        # in it and return it.
        if path_segment.startswith('/'):
            return UrlEncoded(path_segment, skip_encode=skip_encode)

        # path_segment is relative, so we need a namespace to build an
        # absolute path.
        if owner or app or sharing:
            ns = namespace(owner=owner, app=app, sharing=sharing)
        else:
            ns = self.namespace

        # If no app or owner are specified, then use the /services
        # endpoint. Otherwise, use /servicesNS with the specified
        # namespace. If only one of app and owner is specified, use
        # '-' for the other.
        if ns.app is None and ns.owner is None:
            return UrlEncoded(f"/services/{path_segment}", skip_encode=skip_encode)

        oname = "nobody" if ns.owner is None else ns.owner
        aname = "system" if ns.app is None else ns.app
        path = UrlEncoded(f"/servicesNS/{oname}/{aname}/{path_segment}", skip_encode=skip_encode)
        return path
