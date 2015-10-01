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

"""Utility module shared by the SDK examples & unit tests."""

from utils.cmdopts import *

def config(option, opt, value, parser):
    assert opt == "--config"
    parser.load(value)

# Default Splunk cmdline rules
RULES_SPLUNK = {
    'config': {
        'flags': ["--config"],
        'action': "callback",
        'callback': config,
        'type': "string",
        'nargs': "1",
        'help': "Load options from config file" 
    },
    'scheme': {
        'flags': ["--scheme"],
        'default': "https",
        'help': "Scheme (default 'https')",
    },
    'host': {
        'flags': ["--host"],
        'default': "localhost",
        'help': "Host name (default 'localhost')" 
    },
    'port': { 
        'flags': ["--port"],
        'default': "8089",
        'help': "Port number (default 8089)" 
    },
    'app': {
        'flags': ["--app"], 
        'help': "The app context (optional)"
    },
    'owner': {
        'flags': ["--owner"], 
        'help': "The user context (optional)"
    },
    'username': {
        'flags': ["--username"],
        'default': None,
        'help': "Username to login with" 
    },
    'password': {
        'flags': ["--password"], 
        'default': None,
        'help': "Password to login with" 
    },
    'version': {
        'flags': ["--version"],
        'default': None,
        'help': 'Ignore. Used by JavaScript SDK.'
    }
}

FLAGS_SPLUNK = RULES_SPLUNK.keys()

# value: dict, args: [(dict | list | str)*]
def dslice(value, *args):
    """Returns a 'slice' of the given dictionary value containing only the
       requested keys. The keys can be requested in a variety of ways, as an
       arg list of keys, as a list of keys, or as a dict whose key(s) represent
       the source keys and whose corresponding values represent the resulting 
       key(s) (enabling key rename), or any combination of the above.""" 
    result = {}
    for arg in args:
        if isinstance(arg, dict):
            for k, v in arg.iteritems():
                if value.has_key(k): 
                    result[v] = value[k]
        elif isinstance(arg, list):
            for k in arg:
                if value.has_key(k): 
                    result[k] = value[k]
        else:
            if value.has_key(arg): 
                result[arg] = value[arg]
    return result

def parse(argv, rules=None, config=None, **kwargs):
    """Parse the given arg vector with the default Splunk command rules."""
    parser_ = parser(rules, **kwargs)
    if config is not None: parser_.loadrc(config)
    return parser_.parse(argv).result

def parser(rules=None, **kwargs):
    """Instantiate a parser with the default Splunk command rules."""
    rules = RULES_SPLUNK if rules is None else dict(RULES_SPLUNK, **rules)
    return Parser(rules, **kwargs)

