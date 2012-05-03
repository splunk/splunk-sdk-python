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

from xml.etree.ElementTree import XML

from splunklib.data import record

__all__ = [
    "connect",
    "Context",
    "handler",
    "HTTPError",
]

DEFAULT_HOST = "localhost"
DEFAULT_PORT = "8089"
DEFAULT_SCHEME = "https"

def prefix(**kwargs):
    """Returns a URL prefix (such as *https://localhost:8089*) that is 
    constructed from the arguments you provide.

    :param `scheme`: The URL scheme (*http* or *https*).
    :param `host`: The host name.
    :param `port`: The port number.
    :return: The URL prefix.
    """
    scheme = kwargs.get("scheme", DEFAULT_SCHEME)
    host = kwargs.get("host", DEFAULT_HOST)
    port = kwargs.get("port", DEFAULT_PORT)
    if ':' in host: host = '[' + host + ']' # Encode ipv6 address literal
    return "%s://%s:%s" % (scheme, host, port)

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
        self.prefix = prefix(**kwargs)
        self.scheme = kwargs.get("scheme", DEFAULT_SCHEME)
        self.host = kwargs.get("host", DEFAULT_HOST)
        self.port = kwargs.get("port", DEFAULT_PORT)
        self.namespace = namespace(**kwargs)
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")

    # Shared per-context request headers
    def _headers(self):
        return [("Authorization", self.token)]

    def connect(self):
        """Returns an open connection (socket) to the service."""
        cn = socket.create_connection((self.host, int(self.port)))
        return ssl.wrap_socket(cn) if self.scheme == "https" else cn

    def delete(self, path, **kwargs):
        """Issues a ``DELETE`` request to a REST endpoint you specify.
        
        :param `path`: The resource path (REST endpoint).
        :param `kwargs`: Request arguments (optional).
        """
        return self.http.delete(self.url(path), self._headers(), **kwargs)

    def get(self, path, **kwargs):
        """Issues a ``GET`` request to a REST endpoint you specify.

        :param `path`: The resource path (REST endpoint). 
        :param `kwargs`: Query arguments (optional).
        """
        return self.http.get(self.url(path), self._headers(), **kwargs)

    def post(self, path, **kwargs):
        """Issues a ``POST`` request to a REST endpoint you specify.

        :param `path`: The resource path (REST endpoint). 
        :param `kwargs`: Form arguments (optional).
        """
        return self.http.post(self.url(path), self._headers(), **kwargs)

    def request(self, path, message):
        """Issues an ``HTTP`` request message to a REST endpoint you specify.
        
        :param `path`: The resource path (REST endpoint). 
        :param `request`: The request message.
        """
        return self.http.request(
            self.url(path), {
                'method': message.get("method", "GET"),
                'headers': message.get("headers", []) + self._headers(),
                'body': message.get("body", "")})

    def login(self):
        """Issues a Splunk login request using the context's credentials and
        stores the session token for use on subsequent requests.
        """
        response = self.http.post(
            self.url("/services/auth/login"),
            username=self.username, 
            password=self.password)
        body = response.body.read()
        session = XML(body).findtext("./sessionKey")
        self.token = "Splunk %s" % session
        return self

    def logout(self):
        """Forgets the current session token."""
        self.token = None
        return self

    def fullpath(self, path, **kwargs):
        """Returns a full REST endpoint using an endpoint path or path fragment,
        then adds namespace segments by either using any namespace arguments 
        that are provided or the context namespace values.
        
        :param `path`: The resource path (REST endpoint), possibly a fragment.
        :param `kwargs`: Namespace arguments to use for completing the path: 
                         *sharing*, *owner*, and *app* (optional).
        """
        if path.startswith('/'): 
            return path

        # Use namespace kwargs if any provided, otherwise use context defaults
        if 'app' in kwargs or 'owner' in kwargs or 'sharing' in kwargs:
            ns = namespace(**kwargs)
        else:
            ns = self.namespace

        # If no app or owner are specified, then use the /services endpoint
        if ns.app is None and ns.owner is None:
            return "/services/%s" % urllib.quote(path)

        # At least one of app or owner is specified, so use the /serviceNS
        # endpoint and if only one is specified, then wildcard the other.
        oname = "-" if ns.owner is None else ns.owner
        aname = "-" if ns.app is None else ns.app
        return "/servicesNS/%s/%s/%s" % (urllib.quote(oname), 
                                         urllib.quote(aname),
                                         urllib.quote(path))

    # Convert the given path into a fully qualified URL by first qualifying
    # the given path with namespace segments if necessarry and then prefixing
    # with the scheme, host and port.
    def url(self, path):
        """Converts a REST endpoint (from a path or path fragment) into a 
        complete URL.

        :param `path`: The resource path (REST endpoint) to convert to a full 
                       URL.
        """
        return self.prefix + self.fullpath(path)

# kwargs: scheme, host, port, app, owner, username, password
def connect(**kwargs):
    """Establishes an authenticated context with the host.

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
            url = url + '?' + encode(**kwargs)
        message = {
            'method': "DELETE",
            'headers': headers,
        }
        return self.request(url, message)

    def get(self, url, headers=None, **kwargs):
        if headers is None: headers = []
        if kwargs: 
            url = url + '?' + encode(**kwargs)
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
    def __init__(self, response):
        self._response = response

    def __str__(self):
        return self.read()

    def close(self):
        self._response.close()

    def read(self, size = None):
        return self._response.read(size)

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
