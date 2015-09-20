#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
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

"""Example of a HTTP request handler that validates server certificates."""

#
# In order to run this sample, you need to supply the path to the server
# root cert file on the command line, eg:
#
#     > python handler_certs.py --ca_file=cacert.pem
#
# For your convenience the Splunk cert file (cacert.pem) is included in this
# directory. There is also a version of the file (cacert.bad.pem) that does
# not match, so that you can check and make sure the validation fails when
# that cert file is ues.
#
# If you run this script without providing the cert file it will simply
# invoke Splunk without anycert validation.
# 

import httplib
from pprint import pprint
from StringIO import StringIO
import ssl
import socket
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import urllib

import splunklib.client as client

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

RULES = {
    "ca_file": {
        'flags': ["--ca_file"],
        'default': None,
        'help': "Root certs file",
    }
}

# Extend httplib's implementation of HTTPSConnection with support server
# certificate validation.
class HTTPSConnection(httplib.HTTPSConnection):
    def __init__(self, host, port=None, ca_file=None):
        httplib.HTTPSConnection.__init__(self, host, port)
        self.ca_file = ca_file

    def connect(self):
        sock = socket.create_connection((self.host, self.port))
        if self.ca_file is not None:
            self.sock = ssl.wrap_socket(
                sock, None, None, 
                ca_certs=self.ca_file, 
                cert_reqs=ssl.CERT_REQUIRED)
        else:
            self.sock = ssl.wrap_socket(
                sock, None, None, cert_reqs=ssl.CERT_NONE)

# Crack the given url into (scheme, host, port, path)
def spliturl(url):
    scheme, opaque = urllib.splittype(url)
    netloc, path = urllib.splithost(opaque)
    host, port = urllib.splitport(netloc)
    # Strip brackets if its an IPv6 address
    if host.startswith('[') and host.endswith(']'): host = host[1:-1]
    if port is None: port = DEFAULT_PORT
    return scheme, host, port, path

def handler(ca_file=None):
    """Returns an HTTP request handler configured with the given ca_file."""

    def request(url, message, **kwargs):
        scheme, host, port, path = spliturl(url)

        if scheme != "https": 
            ValueError("unsupported scheme: %s" % scheme)

        connection = HTTPSConnection(host, port, ca_file)
        try:
            body = message.get('body', "")
            headers = dict(message.get('headers', []))
            connection.request(message['method'], path, body, headers)
            response = connection.getresponse()
        finally:
            connection.close()

        return {
            'status': response.status,
            'reason': response.reason,
            'headers': response.getheaders(),
            'body': StringIO(response.read())
        }

    return request

opts = utils.parse(sys.argv[1:], RULES, ".splunkrc")
ca_file = opts.kwargs['ca_file']
service = client.connect(handler=handler(ca_file), **opts.kwargs)
pprint([app.name for app in service.apps])

