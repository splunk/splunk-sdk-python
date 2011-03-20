# Copyright 2011 Splunk, Inc.
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

"""Low-level 'binding' interface to the Splunk REST API."""

import httplib
import socket
import ssl
import urllib

from xml.etree.ElementTree import XML

from splunk.data import record

__all__ = [
    "connect",
    "Context",
    "handler",
    "HTTPError",
]

DEFAULT_HOST = "localhost"
DEFAULT_PORT = "8089"
DEFAULT_SCHEME = "https"

# Construct an URL prefix from the given scheme, host and port.
# kwargs: scheme, host, port
def prefix(**kwargs):
    scheme = kwargs.get("scheme", DEFAULT_SCHEME)
    host = kwargs.get("host", DEFAULT_HOST)
    port = kwargs.get("port", DEFAULT_PORT)
    return "%s://%s:%s" % (scheme, host, port)

class Context:
    # kwargs: scheme, host, port, username, password, namespace
    def __init__(self, handler=None, **kwargs):
        self.http = HttpLib(handler)
        self.token = None
        self.prefix = prefix(**kwargs)
        self.scheme = kwargs.get("scheme", DEFAULT_SCHEME)
        self.host = kwargs.get("host", DEFAULT_HOST)
        self.port = kwargs.get("port", DEFAULT_PORT)
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")
        self.namespace = kwargs.get("namespace", None)

    # Shared per-context request headers
    def _headers(self):
        return [("Authorization", self.token)]

    def connect(self):
        """Open a connection (socket) to the service (host:port)."""
        cn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cn.connect((self.host, int(self.port)))
        return ssl.wrap_socket(cn) if self.scheme == "https" else cn

    def delete(self, path, **kwargs):
        """Issue a DELETE request to the given path."""
        return self.http.delete(self.url(path), self._headers(), **kwargs)

    def get(self, path, **kwargs):
        """Issue a GET request to the given path."""
        return self.http.get(self.url(path), self._headers(), **kwargs)

    def post(self, path, **kwargs):
        """Issue a POST request to the given path."""
        return self.http.post(self.url(path), self._headers(), **kwargs)

    def request(self, path, message):
        """Issue the given HTTP request message to the given endpoint."""
        return self.http.request(
            self.url(path), {
                'method': message.get("method", "GET"),
                'headers': message.get("headers", []) + self._headers(),
                'body': message.get("body", "")})

    def login(self):
        """Issue a Splunk login request using the context's credentials and
           store the session token for use on subsequent requests."""
        response = self.http.post(
            self.url("/services/auth/login"),
            username=self.username, 
            password=self.password)
        body = response.body.read()
        session = XML(body).findtext("./sessionKey")
        self.token = "Splunk %s" % session
        return self

    def logout(self):
        """Forget the current session token."""
        self.token = None
        return self

    def fullpath(self, path):
        """If the given path is a fragment, qualify with segments corresponding
           to the binding context's namespace."""
        if path.startswith('/'): 
            return path
        if self.namespace is None: 
            return "/services/%s" % path
        username, appname = self.namespace.split(':')
        if username == "*": 
            username = '-'
        if appname == "*": 
            appname = '-'
        return "/servicesNS/%s/%s/%s" % (username, appname, path)

    # Convet the given path into a fully qualified URL by first qualifying
    # the given path with namespace segments if necessarry and then prefixing
    # with the scheme, host and port.
    def url(self, path):
        """Converts the given path or path fragment into a complete URL."""
        return self.prefix + self.fullpath(path)

# kwargs: scheme, host, port, username, password, namespace
def connect(**kwargs):
    """Establishes an authenticated context with the given host."""
    return Context(**kwargs).login() 

# Note: the error response schema supports multiple messages but we only
# return the first, although we do return the body so that an exception 
# handler that wants to read multiple messages can do so.
def read_error_message(response):
    body = response.body.read()
    return body, XML(body).findtext("./messages/msg")

class HTTPError(Exception):
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
# The HTTP interface used by the Splunk binding layer abstracts the unerlying
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
    scheme, part = url.split(':', 1)
    host, path = urllib.splithost(part)
    host, port = urllib.splitnport(host, 80)
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

    def request(self, url, headers=None, **kwargs):
        response = self.handler(url, headers, **kwargs)
        response = record(response)
        if 400 <= response.status:
            raise HTTPError(response) 
        return response

# Converts an httplib response into a file-like object.
class ResponseReader:
    def __init__(self, response):
        self._response = response

    def __str__(self):
        return self.read()

    def read(self, size = None):
        return self._response.read(size)

# The default HTTP request handler.
def handler(key_file=None, cert_file=None, timeout=None):
    """Creates an HTTP request handler parameterized with the given args."""

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
