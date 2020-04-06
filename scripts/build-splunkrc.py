# Copyright 2011-2020 Splunk, Inc.
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

#!/usr/bin/env python

import sys
import json
import urllib.parse
import os
from pathlib import Path
from string import Template

DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': '8089',
    'username': 'admin',
    'password': 'changeme',
    'scheme': 'https',
    'version': '6.3'
}

DEFAULT_SPLUNKRC_PATH = os.path.join(str(Path.home()), '.splunkrc')

SPLUNKRC_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'templates/splunkrc.template')

# {
#     "server_roles": {
#         "standalone": [
#             {
#                 "host": "10.224.106.158",
#                 "ports": {
#                     "8089/tcp": "10.224.106.158:55759",
#                 },
#                 "splunk": {
#                     "user_roles": {
#                         "admin": {
#                             "password": "Chang3d!",
#                             "username": "admin"
#                         }
#                     },
#                     "version": "8.1.0",
#                     "web_url": "http://10.224.106.158:55761"
#                 }
#             }
#         ]
#     }
# }
def build_config(json_string):
    try:
        spec_config = json.loads(json_string)

        server_config = spec_config['server_roles']['standalone'][0]
        splunk_config = server_config['splunk']

        host, port = parse_hostport(server_config['ports']['8089/tcp'])

        return {
            'host': host,
            'port': port,
            'username': splunk_config['user_roles']['admin']['username'],
            'password': splunk_config['user_roles']['admin']['password'],
            'version': splunk_config['version'],
        }
    except Exception as e:
        raise ValueError('Invalid configuration JSON string') from e

# Source: https://stackoverflow.com/a/53172593
def parse_hostport(host_port):
    # urlparse() and urlsplit() insists on absolute URLs starting with "//"
    result = urllib.parse.urlsplit('//' + host_port)
    return result.hostname, result.port

def run(variable, splunkrc_path=None):
    # read JSON from input
    # parse the JSON
    input_config = build_config(variable) if variable else DEFAULT_CONFIG

    config = {**DEFAULT_CONFIG, **input_config}

    # build a splunkrc file
    with open(SPLUNKRC_TEMPLATE_PATH, 'r') as f:
        template = Template(f.read())

    splunkrc_string = template.substitute(config)

    # if no splunkrc, dry-run
    if not splunkrc_path:
        print(splunkrc_string)
        return

    # write the .splunkrc file
    with open(splunkrc_path, 'w') as f:
        f.write(splunkrc_string)

if sys.stdin.isatty():
    DATA = None
else:
    DATA = sys.stdin.read()

run(DATA, sys.argv[1] if len(sys.argv) > 1 else None)
