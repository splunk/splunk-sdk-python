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

"""Example of a urllib2 based HTTP request handler."""

from pprint import pprint
from StringIO import StringIO
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import urllib2
import ssl

import splunklib.client as client

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

def request(url, message, **kwargs):
    method = message['method'].lower()
    data = message.get('body', "") if method == 'post' else None
    headers = dict(message.get('headers', []))
    # If running Python 2.7.9+, disable SSL certificate validation
    req = urllib2.Request(url, data, headers)
    try:
        if sys.version_info >= (2, 7, 9):
            response = urllib2.urlopen(req, context=ssl._create_unverified_context())
        else:
            response = urllib2.urlopen(req)
    except urllib2.HTTPError, response:
        pass # Propagate HTTP errors via the returned response message
    return {
        'status': response.code,
        'reason': response.msg,
        'headers': response.info().dict,
        'body': StringIO(response.read())
    }

opts = utils.parse(sys.argv[1:], {}, ".splunkrc")
service = client.connect(handler=request, **opts.kwargs)
pprint([app.name for app in service.apps])

