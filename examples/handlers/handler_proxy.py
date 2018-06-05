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

"""Example of a HTTP request handler that supports requests via a HTTP proxy."""

#
# In order to run this sample, you will need to have a proxy available to
# relay your requests to Splunk. One way to do this is to run the tiny-proxy.py
# script included in this directory and then run this script using whatever
# port you bound tiny-proxy to, eg:
#
#     > python tiny-proxy.py -p 8080
#     > python handler_proxy.py --proxy=localhost:8080
# 

from __future__ import absolute_import

from io import BytesIO
from pprint import pprint
import sys, os
import ssl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from splunklib.six.moves import urllib

import splunklib.client as client

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

RULES = {
    "proxy": {
        'flags': ["--proxy"],
        'default': "localhost:8080",
        'help': "Use proxy on given <host[:port]> (default localhost:8080)",
    }
}

def request(url, message, **kwargs):
    method = message['method'].lower()
    data = message.get('body', "") if method == 'post' else None
    headers = dict(message.get('headers', []))
    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as response:
        # If running Python 2.7.9+, disable SSL certificate validation and try again
        if sys.version_info >= (2, 7, 9):
            response = urllib.request.urlopen(req, context=ssl._create_unverified_context())
        else:
            raise
    except urllib.error.HTTPError as response:
        pass # Propagate HTTP errors via the returned response message
    return {
        'status': response.code,
        'reason': response.msg,
        'headers': dict(response.info()),
        'body': BytesIO(response.read().encode('utf-8'))
    }

def handler(proxy):
    proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    return request

opts = utils.parse(sys.argv[1:], RULES, ".splunkrc")
proxy = opts.kwargs['proxy']
try:
    service = client.connect(handler=handler(proxy), **opts.kwargs)
    pprint([app.name for app in service.apps])
except urllib.error.URLError as e:
    if e.reason.errno == 1 and sys.version_info < (2, 6, 3):
        # There is a bug in Python < 2.6.3 that does not allow proxies with
        # HTTPS. You can read more at: http://bugs.python.org/issue1424152
        pass
    else:
        raise

