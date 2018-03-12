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

"""Retrieves a list of installed apps from Splunk by making REST API calls
   using Python's httplib module."""

from __future__ import absolute_import
from __future__ import print_function
import splunklib.six.moves.http_client
import urllib
from xml.etree import ElementTree

HOST = "localhost"
PORT = 8089
USERNAME = "admin"
PASSWORD = "changeme"

# Present credentials to Splunk and retrieve the session key
connection = six.moves.http_client.HTTPSConnection(HOST, PORT)
body = urllib.urlencode({'username': USERNAME, 'password': PASSWORD})
headers = { 
    'Content-Type': "application/x-www-form-urlencoded", 
    'Content-Length': str(len(body)),
    'Host': HOST,
    'User-Agent': "a.py/1.0",
    'Accept': "*/*"
}
try:
    connection.request("POST", "/services/auth/login", body, headers)
    response = connection.getresponse()
finally:
    connection.close()
if response.status != 200:
    raise Exception("%d (%s)" % (response.status, response.reason))
body = response.read()
sessionKey = ElementTree.XML(body).findtext("./sessionKey")

# Now make the request to Splunk for list of installed apps
connection = six.moves.http_client.HTTPSConnection(HOST, PORT)
headers = { 
    'Content-Length': "0",
    'Host': HOST,
    'User-Agent': "a.py/1.0",
    'Accept': "*/*",
    'Authorization': "Splunk %s" % sessionKey,
}
try:
    connection.request("GET", "/services/apps/local", "", headers)
    response = connection.getresponse()
finally:
    connection.close()
if response.status != 200:
    raise Exception("%d (%s)" % (response.status, response.reason))

body = response.read()
data = ElementTree.XML(body)
apps = data.findall("{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}title")
for app in apps: 
    print(app.text)
