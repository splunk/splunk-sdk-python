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

from pprint import pprint

import base64
from getpass import getpass
import httplib
import json
import socket
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


import splunklib.client as client

from utils import error, parse

TWITTER_STREAM_HOST = "stream.twitter.com"
TWITTER_STREAM_PATH = "/1/statuses/sample.json"

DEFAULT_SPLUNK_HOST = "localhost"
DEFAULT_SPLUNK_PORT = 9001

ingest = None       # The splunk ingest socket
verbose = 1

class Twitter:
    def __init__(self, username, password):
        self.buffer = ""
        self.username = username
        self.password = password

    def connect(self):
        # Login using basic auth
        login = "%s:%s" % (self.username, self.password)
        token = "Basic " + str.strip(base64.encodestring(login))
        headers = {
            'Content-Length': "0",
            'Authorization': token,
            'Host': "stream.twitter.com",
            'User-Agent': "twitted.py/0.1",
            'Accept': "*/*",
        }
        connection = httplib.HTTPSConnection(TWITTER_STREAM_HOST)
        connection.request("GET", TWITTER_STREAM_PATH, "", headers)
        response = connection.getresponse()
        if response.status != 200:
            raise Exception, "HTTP Error %d (%s)" % (
                response.status, response.reason)
        return response

RULES = {
    'tusername': {
        'flags': ["--twitter:username"],
        'help': "Twitter username",
    },
    'tpassword': { 
        'flags': ["--twitter:password"],
        'help': "Twitter password",
    },
    'inputhost': {
        'flags': ["--input:host"],
        'help': "Host address for Splunk (default: localhost)",
    },
    'inputport': {
        'flags': ["--input:port"],
        'help': "Port to use for Splunk TCP input (default: 9001)",
    },
    'verbose': {
        'flags': ["--verbose"],
        'default': 1,
        'type': "int",
        'help': "Verbosity level (0-3, default 0)",
    }
}

def cmdline():
    kwargs = parse(sys.argv[1:], RULES, ".splunkrc").kwargs

    # Prompt for Twitter username/password if not provided on command line
    if not kwargs.has_key('tusername'):
        kwargs['tusername'] = raw_input("Twitter username: ")
    if not kwargs.has_key('tpassword'):
        kwargs['tpassword'] = getpass("Twitter password:")

    # Prompt for Splunk username/password if not provided on command line
    if not kwargs.has_key('username'):
        kwargs['username'] = raw_input("Splunk username: ")
    if not kwargs.has_key('password'):
        kwargs['password'] = getpass("Splunk password:")

    return kwargs

# Returns a str, dict or simple list
def flatten(value, prefix=None):
    """Takes an arbitrary JSON(ish) object and 'flattens' it into a dict
       with values consisting of either simple types or lists of simple
       types."""

    def issimple(value): # foldr(True, or, value)?
        for item in value:
            if isinstance(item, dict) or isinstance(item, list):
                return False
        return True

    if isinstance(value, unicode):
        return value.encode("utf8")

    if isinstance(value, list):
        if issimple(value): return value
        offset = 0
        result = {}
        prefix = "%d" if prefix is None else "%s_%%d" % prefix
        for item in value:
            k = prefix % offset
            v = flatten(item, k)
            if not isinstance(v, dict): v = {k:v}
            result.update(v)
            offset += 1
        return result

    if isinstance(value, dict):
        result = {}
        prefix = "%s" if prefix is None else "%s_%%s" % prefix
        for k, v in value.iteritems():
            k = prefix % str(k)
            v = flatten(v, k)
            if not isinstance(v, dict): v = {k:v}
            result.update(v)
        return result

    return value

# Sometimes twitter just stops sending us data on the HTTP connection.
# In these cases, we'll try up to MAX_TRIES to read 2048 bytes, and if 
# that fails we bail out.
MAX_TRIES = 100

def listen(username, password):
    try:
        twitter = Twitter(username, password)
        stream = twitter.connect()
    except Exception as e:
        error("There was an error logging in to Twitter:\n%s" % str(e), 2)

    buffer = ""
    tries = 0
    while True and tries < MAX_TRIES:
        offset = buffer.find("\r\n")
        if offset != -1:
            status = buffer[:offset]
            buffer = buffer[offset+2:]
            process(status)
            tries = 0
            continue # Consume all statuses in buffer before reading more
        buffer += stream.read(2048)
        tries += 1

    if tries == MAX_TRIES:
        error("""Twitter seems to have closed the connection. Make sure 
you don't have any other open instances of the 'twitted' sample app.""", 2)

def output(record):
    print_record(record)

    for k in sorted(record.keys()):
        if k.endswith("_str"): 
            continue # Ignore

        v = record[k]

        if v is None:
            continue # Ignore

        if isinstance(v, list):
            if len(v) == 0: continue
            v = ','.join([str(item) for item in v])

        # Field renames
        k = { 'source': "status_source" }.get(k, k)

        if isinstance(v, str):
            format = '%s="%s" '
            v = v.replace('"', "'")
        else:
            format = "%s=%r "
        result = format % (k, v)

        ingest.send(result)

    end = "\r\n---end-status---\r\n"
    try: 
        ingest.send(end)
    except:
        error("There was an error with the TCP connection to Splunk.", 2)

# Print some infor to stdout, depending on verbosity level.
def print_record(record):
    if verbose == 0: 
        return

    if verbose > 1:
        pprint(record) # Very chatty
        return

    # Otherwise print a nice summary of the record
    if record.has_key('delete_status_id'):
        print "delete %d %d" % (
            record['delete_status_id'],
            record['delete_status_user_id'])
    else:
        print "status %s %d %d" % (
            record['created_at'], 
            record['id'], 
            record['user_id'])

def process(status):
    status = json.loads(status)
    record = flatten(status)
    output(record)

def main():
    kwargs = cmdline()

    global verbose
    verbose = kwargs['verbose']

    # Force the owner namespace, if not provided
    if 'owner' not in kwargs.keys():
        kwargs['owner'] = kwargs['username']

    if verbose > 0: print "Initializing Splunk .."
    service = client.connect(**kwargs)

    # Create the index if it doesn't exist
    if 'twitter' not in service.indexes:
        if verbose > 0: print "Creating index 'twitter' .."
        service.indexes.create("twitter")

    # Create the TCP input if it doesn't exist
    input_host = kwargs.get("inputhost", DEFAULT_SPLUNK_HOST)
    input_port = kwargs.get("inputport", DEFAULT_SPLUNK_PORT)
    input_name = str(input_port)
    if input_name not in service.inputs:
        if verbose > 0: print "Creating input '%s'" % input_name
        service.inputs.create(
            input_port, "tcp", index="twitter", sourcetype="twitter")
    
    global ingest
    ingest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ingest.connect((input_host, input_port))

    if verbose > 0: 
        print "Listening (and sending data to %s:%s).." % (input_host, input_port)
    try: 
        listen(kwargs['tusername'], kwargs['tpassword'])
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error("""There was an error with the connection to Twitter. Make sure
you don't have other running instances of the 'twitted' sample app, and try 
again.""", 2)
        print e
        
if __name__ == "__main__":
    main()

