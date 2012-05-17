# Copyright 2011-2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""This module contains a low-level *binding* interface to the `Splunk REST API
<http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTcontents>`_.

This module is designed to enable client-side interaction with the Splunk
REST API at the level of HTTP requests and responses, and it provides simple
helpers for things like Splunk authentication and the use of Splunk namespaces.

This module is specifically designed to be lightweight and faithful to the 
underlying Splunk REST API. If you want a friendlier interface to the Splunk 
REST API, consider using the :mod:`splunklib.client` module.
"""

#
# A note on namespaces:
#
# Every Splunk resource belongs to a namespace. The namespace is specified by
# the pair of values `owner` and `app` and is governed by a `sharing` mode. 
# The possible values for `sharing` are: "user", "app", "global" and "system", 
# which map to the following combinations of `owner` and `app` values.
#
#     `user`   => {owner}, {app}
#     `app`    => nobody, {app}
#     `global` => nobody, {app}
#     `system` => nobody, system
#
# `nobody` is a special user name that basically means no-user and `system` is 
# the name reserved for system resources.
#
# "-" is a wildcard that can be used for both `owner` and `app` values and
# refers to all users and all apps, respectively.
#
# In general, when you specify a namespace you can specify any combination of 
# these three values and the library will reconcile the triple, overriding the
# provided values as appropriate.
#
# Finally, if no namespacing is specified the library will make use of the
# `/services` branch of the REST API which provides a namespaced view of
# Splunk resources equivelent to using owner={currentUser} and app={defaultApp}
#

import httplib
import socket
import ssl
import urllib

from contextlib import contextmanager

from xml.etree.ElementTree import XML

from splunklib.data import record

__all__ = [
    "connect",
    "Context",
    "handler",
    "HTTPError",
]

# If you change these, update the docstring 
# on _authority as well.
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "8089"
DEFAULT_SCHEME = "https"

class AuthenticationError(Exception):
    pass

class UrlEncoded(str):
    """String subclass to represent URL encoded strings.

    It's too difficult to track what strings might be URL encoded and
    which not by hand, so eschew any calls to ``urllib.quote``.
    ``urllib.unquote`` any URL encoded strings that arrive from
    outside as soon as you read them, and then wrap any string you
    intend to use as a URL in ``UrlEncoded``. ``UrlEncoded`` is
    idempotent, unlike ``urllib.quote``, so you don't have to worry
    about multiple calls. For example,::

        def f(s):
            ... # do something, but don't call urllib.quote
            return UrlEncoded(...)

    ``UrlEncoded`` objects are identical to ``str`` objects (including
    being equals if their contents are equal) except when passed to
    ``UrlEncoded`` again.

    ``UrlEncoded`` removes ``str``'s support for interpolating values
    with ``%`` (it will raise a ``TypeError`` if you try it). There is
    no reliable way to encode values thus. Instead, interpolate into a
    string, quoting by hand, and call ``UrlEncode`` with
    ``skip_encode=True``, as in::

        import urllib
        UrlEncode('%s://%s' % (scheme, urllib.quote(host)), skip_encode=True)
    """
    def __new__(self, val='', skip_encode=False):
        if isinstance(val, UrlEncoded):
            # Don't urllib.quote something already URL encoded.
            return val
        elif skip_encode:
            return str.__new__(self, val)
        else:
            # When subclassing str, just call str's __new__ method
            # with your class and the value you want to have in the
            # new string.
            return str.__new__(self, urllib.quote(val))

    def __add__(self, other):
        if isinstance(other, UrlEncoded):
            return UrlEncoded(str.__add__(self, other), skip_encode=True)
        else:
            return UrlEncoded(str.__add__(self, urllib.quote(other)), skip_encode=True)

    def __radd__(self, other):
        if isinstance(other, UrlEncoded):
            return UrlEncoded(str.__radd__(self, other), skip_encode=True)
        else:
            return UrlEncoded(str.__add__(urllib.quote(other), self), skip_encode=True)

    def __mod__(self, fields):
        raise TypeError("Cannot interpolate into a UrlEncoded object.")

@contextmanager
def _handle_auth_error(msg):
    """Handle reraising HTTP authentication errors as something clearer.

    If an ``HTTPError`` is raised with status 401 (access denied) in
    the body of this context manager, reraise it as an
    ``AuthenticationError`` instead, with *msg* as its message.

    This function adds no round trips to the server.

    :param msg: The message to be raised in ``AuthenticationError``.
    :type msg: ``str``

    **Example**::

        with _handle_auth_error("Your login failed."):
             ... # make an HTTP request
    """
    try:
        yield
    except HTTPError as he:
        if he.status == 401:
            raise AuthenticationError(msg)
        else:
            raise

def _authority(scheme=DEFAULT_SCHEME, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Construct a URL authority from the given *scheme*, *host*, and *port*.

    Named in accordance with RFC2396_, which defines URLs as::

        <scheme>://<authority><path>?<query>

    .. _RFC2396: http://www.ietf.org/rfc/rfc2396.txt

    So ``https://localhost:8000/a/b/b?boris=hilda`` would be parsed as::

        scheme := https
        authority := localhost:8000
        path := /a/b/c
        query := boris=hilda

    :param scheme: URL scheme (default: ``"https"``)
    :type scheme: ``"http"`` or ``"https"``
    :param host: The host name (default: ``"localhost"``)
    :type host: string
    :param port: The port number (default: 8089)
    :type port: integer
    :return: The URL authority.
    :rtype: UrlEncoded (subclass of ``str``)

    **Example**::

        _authority() == "https://localhost:8089"

        _authority(host="splunk.utopia.net") == "https://splunk.utopia.net:8089"

        _authority(host="2001:0db8:85a3:0000:0000:8a2e:0370:7334") == \
            "https://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:8089"

        _authority(scheme="http", host="splunk.utopia.net", port="471") == \
            "http://splunk.utopia.net:471"
        
    """
    if ':' in host: 
        # IPv6 addresses must be enclosed in [ ] in order to be well
        # formed.
        host = '[' + host + ']'
    return UrlEncoded("%s://%s:%s" % (scheme, host, port), skip_encode=True)

# kwargs: sharing, owner, app
def namespace(**kwargs):
    """Returns a reconciled dictionary of namespace values built from the 
    arguments you provide.

    :param `sharing`: The sharing mode: *system*, *global*, *app*, or *user*
                      (the default is *user*). 
    :param `owner`: The owner context (optional).
    :param `app`: The app context (optional).
    """
    sharing = kwargs.get('sharing', None)
    if sharing in ["system"]:
        return record({
            'sharing': sharing, 
            'owner': "nobody", 
            'app': "system" })
    if sharing in ["global", "app"]:
        return record({ 
            'sharing': sharing, 
            'owner': "nobody", 
            'app': kwargs.get('app', None)})
    if sharing in ["user", None]:
        return record({
            'sharing': sharing, 
            'owner': kwargs.get('owner', None),
            'app': kwargs.get('app', None)})
    raise ValueError("Invalid value for argument: 'sharing'")

class Context(object):
    """This class provides a binding context to a corresponding Splunk service
    that can be used to issue HTTP requests.
            
    A context also captures an optional namespace context consisting of an
    optional owner name (or "-" wildcard) and optional app name (or "-" 
    wildcard). To use the :class:`Context` class, the instance must be
    authenticated by presenting credentials using the :meth:`login` method
    or by constructing the instance using the :func:`connect` function, which
    both creates and authenticates the instance.

    :param `host`: The host name (the default is *localhost*).
    :param `port`: The port number (the default is *8089*).
    :param `scheme`: The scheme for accessing the service (the default is 
                     *https*).
    :param `owner`: The owner namespace (optional).
    :param `app`: The app context (optional).
    :param `token`: The current session token (optional). Session tokens can be 
                    shared across multiple service instances.
    :param `username`: The Splunk account username, which is used to 
                       authenticate the Splunk instance.
    :param `password`: The password, which is used to authenticate the Splunk 
                       instance.
    :param `handler`: The HTTP request handler (optional).
    """
    def __init__(self, handler=None, **kwargs):        
        self.http = HttpLib(handler)
        self.token = kwargs.get("token", None)
        self.scheme = kwargs.get("scheme", DEFAULT_SCHEME)
        self.host = kwargs.get("host", DEFAULT_HOST)
        self.port = kwargs.get("port", DEFAULT_PORT)
        self.authority = _authority(self.scheme, self.host, self.port)
        self.namespace = namespace(**kwargs)
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        self.autologin = kwargs.get("autologin", False)

    # Shared per-context request headers
    @property
    def _auth_headers(self):
        return [("Authorization", self.token)]

    def connect(self):
        """Returns an open connection (socket) to the service."""
        cn = socket.create_connection((self.host, int(self.port)))
        return ssl.wrap_socket(cn) if self.scheme == "https" else cn

    def handle_authentication(self, request_fun):
        """Wrapper to handle autologin and authentication errors.

        *request_fun* is a function taking no arguments that needs to
        be run with this ``Context`` logged into Splunk.

        ``handle_authentication``'s behavior depends on whether the
        ``autologin`` field of ``Context`` is set to ``True`` or
        ``False``. If it's ``False``, then ``handle_authentication``
        aborts if the ``Context`` is not logged in, and raises an
        ``AuthenticationError`` if an ``HTTPError`` of status 401 is
        raised in *request_fun*. If it's ``True``, then
        ``handle_authentication`` will try at all sensible places to
        log in before issuing the request.

        If ``autologin`` is ``False``, ``handle_authentication`` makes
        one roundtrip to the server if the ``Context`` is logged in,
        or zero if it is not. If ``autologin`` is ``True``, it's less
        deterministic, and may make at most three roundtrips (though
        that would be a truly pathological case).

        :param request_fun: A function of no arguments encapsulating
                            the request to make to the server.

        **Example**::

            import splunklib.binding as binding
            c = binding.connect(..., autologin=True)
            c.logout()
            def f():
                c.get("/services")
                return 42
            print handle_authentication(f)
        """
        if self.token is None:
            # Not yet logged in.
            if self.autologin:
                # This will throw an uncaught
                # AuthenticationError if it fails.
                self.login() 
            else:
                raise AuthenticationError("Request aborted: not logged in.")
        try:
            # Issue the request
            return request_fun()
        except HTTPError as he:
            if he.status == 401 and self.autologin:
                # Authentication failed. Try logging in, and then
                # rerunning the request. If either step fails, throw
                # an AuthenticationError and give up.
                with _handle_auth_error("Autologin failed."):
                    self.login()
                with _handle_auth_error("Autologin succeeded, but there was an auth error on next request. Something's very wrong."):
                    return request_fun()
            elif he.status == 401 and not self.autologin:
                raise AuthenticationError("Request failed: Session is not logged in.")
            else:
                raise

    def delete(self, path_segment, owner=None, app=None, sharing=None, **query):
        """DELETE at *path_segment* with the given namespace and query.

        Named to match the HTTP method. This function makes at least
        one roundtrip to the server, and one additional round trip for
        each 303 status returned.

        If *owner*, *app*, and *sharing* are omitted, then uses this
        ``Context``'s default namespace. All other keyword arguments
        are included in the URL as query parameters.

        :raises AuthenticationError: when a the ``Context`` is not logged in.
        :raises HTTPError: when there was an error in GETting from *path_segment*.
        :param path_segment: A path_segment to GET from.
        :type path_segment: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :param query: All other keyword arguments, used as query parameters.
        :type query: values should be strings
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.delete('saved/searches/boris') == \
                {'body': <splunklib.binding.ResponseReader at 0x10f870ad0>,
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
        def f():
            path = self.authority + self._abspath(path_segment, owner=owner,
                                                  app=app, sharing=sharing)
            return self.http.delete(path, self._auth_headers, **query)
        return self.handle_authentication(f)

    def get(self, path_segment, owner=None, app=None, sharing=None, **query):
        """GET from *path_segment* with the given namespace and query.

        Named to match the HTTP method. This function makes at least
        one roundtrip to the server, and one additional round trip for
        each 303 status returned.

        If *owner*, *app*, and *sharing* are omitted, then uses this
        ``Context``'s default namespace. All other keyword arguments
        are included in the URL as query parameters.

        :raises AuthenticationError: when a the ``Context`` is not logged in.
        :raises HTTPError: when there was an error in GETting from *path_segment*.
        :param path_segment: A path_segment to GET from.
        :type path_segment: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :param query: All other keyword arguments, used as query parameters.
        :type query: values should be strings
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.get('apps/local') == \
                {'body': <splunklib.binding.ResponseReader at 0x10f8709d0>,
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
        def f():
            path = self.authority + self._abspath(path_segment, owner=owner,
                                                  app=app, sharing=sharing)
            return self.http.get(path, self._auth_headers, **query)
        return self.handle_authentication(f)

    def post(self, path_segment, owner=None, app=None, sharing=None, **query):
        """POST to *path_segment* with the given namespace and query.

        Named to match the HTTP method. This function makes at least
        one roundtrip to the server, and one additional round trip for
        each 303 status returned.

        If *owner*, *app*, and *sharing* are omitted, then uses this
        ``Context``'s default namespace. All other keyword arguments
        are included in the URL as query parameters.

        :raises AuthenticationError: when a the ``Context`` is not logged in.
        :raises HTTPError: when there was an error in POSTing to *path_segment*.
        :param path_segment: A path_segment to POST to.
        :type path_segment: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :param query: All other keyword arguments, used as query parameters.
        :type query: values should be strings
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.post('saved/searches', name='boris', 
                   search='search * earliest=-1m | head 1') == \
                {'body': <splunklib.binding.ResponseReader at 0x10f870d50>,
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
        def f():
            path = self.authority + self._abspath(path_segment, owner=owner, 
                                                  app=app, sharing=sharing)
            return self.http.post(path, self._auth_headers, **query)
        return self.handle_authentication(f)

    def request(self, path_segment, method="GET", headers=[], body="",
                owner=None, app=None, sharing=None):
        """Issue an arbitrary HTTP request to *path_segment*.
        
        Named and argumented in analogy to ``httplib.request(...)``.
        Makes a single round trip to the server.

        If *owner*, *app*, and *sharing* are omitted, then uses this
        ``Context``'s default namespace. All other keyword arguments
        are included in the URL as query parameters.

        :raises AuthenticationError: when a the ``Context`` is not logged in.
        :raises HTTPError: when there was an error in GETting from *path_segment*.
        :param path_segment: A path_segment to GET from.
        :type path_segment: string
        :param method: Request method (default: ``"GET"``)
        :type method: ``"GET"``, ``"POST"``, or ``"DELETE"``
        :param headers: Additional headers for the request (authentication 
                        header will be added automatically).
        :type headers: list of (string,string) representing key/value pairs
        :param body: Data to send in the request.
        :type body: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            c = binding.connect(...)
            c.request('saved/searches', method='GET') == \
                {'body': <splunklib.binding.ResponseReader at 0x10b18fa50>,
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
        def f():
            path = self.authority \
                + self._abspath(path_segment, owner=owner, 
                                app=app, sharing=sharing)
            headers = headers + self._auth_headers
            return self.http.request(path,
                                     {'method': method,
                                      'headers': headers,
                                      'body': body})
        return self.handle_authentication(f)

    def login(self):
        """Issues a Splunk login request using the context's credentials and
        stores the session token for use on subsequent requests.
        """
        try:
            response = self.http.post(
                self.authority + self._abspath("/services/auth/login"),
                username=self.username, 
                password=self.password)
            body = response.body.read()
            session = XML(body).findtext("./sessionKey")
            self.token = "Splunk %s" % session
            return self
        except HTTPError as he:
            if he.status == 401:
                raise AuthenticationError("Login failed.")
            else:
                raise

    def logout(self):
        """Forgets the current session token."""
        self.token = None
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
        :type path_segment: string
        :param owner, app, sharing: Components of a namespace (defaults 
                                    to the ``Context``'s namespace if all 
                                    three are omitted)
        :type owner, app, sharing: string
        :return: A ``UrlEncoded`` (a subclass of ``str``).
        :rtype: string

        **Example**::

            import splunklib.binding as binding
            c = binding.connect(owner='boris', app='search', sharing='user')
            c._abspath('/a/b/c') == '/a/b/c'
            c._abspath('/a/b c/d') == '/a/b%20c/d'
            c._abspath('apps/local/search') == \
                '/servicesNS/boris/search/apps/local/search'
            c._abspath('apps/local/search', sharing='systmem') == \
                '/servicesNS/nobody/system/apps/local/search'
            url = c.authority + c._abspath('apps/local/sharing')
        """
        # If path_segment is absolute, escape all forbidden characters
        # in it and return it.
        if path_segment.startswith('/'):
            if isinstance(path_segment, UrlEncoded):
                return path_segment
            else:
                return UrlEncoded(path_segment)

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
            return UrlEncoded("/services/%s" % path_segment)

        oname = "-" if ns.owner is None else ns.owner
        aname = "-" if ns.app is None else ns.app
        return UrlEncoded("/servicesNS/%s/%s/%s" % (oname, aname, path_segment))

# kwargs: scheme, host, port, app, owner, username, password
def connect(**kwargs):
    """Establishes an authenticated context with the host.

    This function makes one round trip to the server.

    :param host: The host name (default: ``"localhost"``).
    :param port: The port number (default: 8089).
    :param scheme: The scheme for accessing the service (default: ``"https"``).
    :param owner: The owner namespace (optional).
    :param app: The app context (optional).
    :param token: The current session token (optional). Session tokens can be 
                  shared across multiple service instances.
    :param username: The Splunk account username, which is used to 
                     authenticate the Splunk instance.
    :param password: The password, which is used to authenticate the Splunk 
                     instance.
    :param autologin: Try to automatically log in again if the session terminates.
    :type autologin: boolean
    :return: An initialized :class:`Context` instance.
    """
    return Context(**kwargs).login() 

# Note: the error response schema supports multiple messages but we only
# return the first, although we do return the body so that an exception 
# handler that wants to read multiple messages can do so.
def read_error_message(response):
    body = response.body.read()
    return body, XML(body).findtext("./messages/msg")

class HTTPError(Exception):
    """This class is raised for HTTP responses that return an error."""
    def __init__(self, response):
        status = response.status
        reason = response.reason
        body, detail = read_error_message(response)
        message = "HTTP %d %s%s" % (
            status, reason, "" if detail is None else " -- %s" % detail)
        Exception.__init__(self, message) 
        self.status = status
        self.reason = reason
        self.headers = response.headers
        self.body = body

#
# The HTTP interface used by the Splunk binding layer abstracts the underlying
# HTTP library using request & response 'messages' which are implemented as
# dictionaries with the following structure:
#
#   # HTTP request message (only method required)
#   request {
#       method : str,
#       headers? : [(str, str)*],
#       body? : str,
#   }
#
#   # HTTP response message (all keys present)
#   response {
#       status : int,
#       reason : str,
#       headers : [(str, str)*],
#       body : file,
#   }
#

# Encode the given kwargs as a query string. This wrapper will also encode 
# a list value as a sequence of assignemnts to the corresponding arg name, 
# for example an argument such as 'foo=[1,2,3]' will be encoded as
# 'foo=1&foo=2&foo=3'. 
def encode(**kwargs):
    items = []
    for key, value in kwargs.iteritems():
        if isinstance(value, list):
            items.extend([(key, item) for item in value])
        else:
            items.append((key, value))
    return urllib.urlencode(items)

# Crack the given url into (scheme, host, port, path)
def spliturl(url):
    scheme, opaque = urllib.splittype(url)
    netloc, path = urllib.splithost(opaque)
    host, port = urllib.splitport(netloc)
    # Strip brackets if its an IPv6 address
    if host.startswith('[') and host.endswith(']'): host = host[1:-1]
    if port is None: port = DEFAULT_PORT
    return scheme, host, port, path

# Given an HTTP request handler, this wrapper objects provides a related
# family of convenience methods built using that handler.
class HttpLib(object):    
    def __init__(self, custom_handler=None):
        self.handler = handler() if custom_handler is None else custom_handler

    def delete(self, url, headers=None, **kwargs):
        if headers is None: headers = []
        if kwargs: 
            # url is already a UrlEncoded. We have to manually declare
            # the query to be encoded or it will get automatically URL
            # encoded by being appended to url.
            url = url + UrlEncoded('?' + encode(**kwargs), skip_encode=True)
        message = {
            'method': "DELETE",
            'headers': headers,
        }
        return self.request(url, message)

    def get(self, url, headers=None, **kwargs):
        if headers is None: headers = []
        if kwargs: 
            # url is already a UrlEncoded. We have to manually declare
            # the query to be encoded or it will get automatically URL
            # encoded by being appended to url.
            url = url + UrlEncoded('?' + encode(**kwargs), skip_encode=True)
        return self.request(url, { 'method': "GET", 'headers': headers })

    def post(self, url, headers=None, **kwargs):
        if headers is None: headers = []
        headers.append(("Content-Type", "application/x-www-form-urlencoded")),
        message = {
            'method': "POST",
            'headers': headers,
            'body': encode(**kwargs)
        }
        return self.request(url, message)

    def request(self, url, message, **kwargs):
        response = self.handler(url, message, **kwargs)
        response = record(response)
        if 400 <= response.status:
            raise HTTPError(response) 
        return response

# Converts an httplib response into a file-like object.
class ResponseReader(object):
    """A file-like interface over ``httplib`` responses.

    ``httplib.HTTPResponse`` is kind of unweildy, and other HTTP
    libraries used with the SDK may be even more different.
    ``ResponseReader`` is a layer meant to unify all of that. It also
    provides lookahead at the stream and a few useful predicates.
    """
    # For testing, you can use a StringIO as the argument to
    # ``ResponseReader`` instead of an ``httplib.HTTPResponse``. It
    # will work equally well.
    def __init__(self, response):
        self._response = response
        self._buffer = ''

    def __str__(self):
        return self.read()

    @property
    def empty(self):
        """Is there any more data in the response?"""
        return self.peek(1) == ""

    def peek(self, size):
        """Nondestructively fetch *size* characters.

        The next ``read`` operation will behave exactly as if ``peek``
        where never called.
        """
        c = self.read(size)
        self._buffer = self._buffer + c
        return c

    def close(self):
        """Close this response."""
        self._response.close()

    def read(self, size = None):
        """Read *size* characters from the response.
        
        If *size* is ``None``, read the whole response.
        """
        r = self._buffer
        self._buffer = ''
        if size is not None:
            size -= len(r)
        r = r + self._response.read(size)
        return r

def handler(key_file=None, cert_file=None, timeout=None):
    """Returns an instance of the default HTTP request handler that uses
    the argument values you provide.

    :param `key_file`: The key file (optional).
    :param `cert_file`: The cert file (optional).
    :param `timeout`: The request time-out period (optional).
    """

    def connect(scheme, host, port):
        kwargs = {}
        if timeout is not None: kwargs['timeout'] = timeout
        if scheme == "http":
            return httplib.HTTPConnection(host, port, **kwargs)
        if scheme == "https":
            if key_file is not None: kwargs['key_file'] = key_file
            if cert_file is not None: kwargs['cert_file'] = cert_file
            return httplib.HTTPSConnection(host, port, **kwargs)
        raise ValueError("unsupported scheme: %s" % scheme)

    def request(url, message, **kwargs):
        scheme, host, port, path = spliturl(url)
        body = message.get("body", "")
        head = { 
            "Content-Length": str(len(body)),
            "Host": host,
            "User-Agent": "splunk-sdk-python/0.1",
            "Accept": "*/*",
        } # defaults
        for key, value in message["headers"]: 
            head[key] = value
        method = message.get("method", "GET")

        connection = connect(scheme, host, port)
        try:
            connection.request(method, path, body, head)
            if timeout is not None: 
                connection.sock.settimeout(timeout)
            response = connection.getresponse()
        finally:
            connection.close()

        return {
            "status": response.status, 
            "reason": response.reason,
            "headers": response.getheaders(),
            "body": ResponseReader(response),
        }

    return request
