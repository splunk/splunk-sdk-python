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

"""A command line utility for manipulating saved searches 
   (list-all/create/list/delete)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import urllib

import splunklib.binding as binding

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

# these 'rules' allow for setting parameters primarily for creating saved searches
RULES = {
    "name": { 
        'flags': ["--name"],
        'help': "<required for all> name of search name to be created" 
    },
    "search": { 
        'flags': ["--search"],
        'help': "<required for create> splunk search string" 
    },
    "is_visible": { 
        'flags': ["--is_visible"],
        'help': "<optional for create> Should the saved search appear under the Seaches & Report menu (defaults to true)"
    },
    "is_scheduled": { 
        'flags': ["--is_scheduled"],
        'help': "<optional for create> Does the saved search run on the saved schedule."
    },
    "max_concurrent": { 
        'flags': ["--max_concurrent"],
        'help': "<optional for create> If the search is ran by the scheduler how many concurrent instances of this search is the scheduler allowed to run (defaults to 1)"
    },
    "realtime_schedule": { 
        'flags': ["--realtime_schedule"],
        'help': "<optional for create> Is the scheduler allowed to skip executions of this saved search, if there is not enough search bandwidtch (defaults to true), set to false only for summary index populating searches"
    },
    "run_on_startup": { 
        'flags': ["--run_on_startup"],
        'help': "<optional for create> Should the scheduler run this saved search on splunkd start up (defaults to false)"
    },
    "cron_schedule": { 
        'flags': ["--cron_schedule"],
        'help': "<optional for create> The cron formatted schedule of the saved search. Required for Alerts"
    },
    "alert_type": { 
        'flags': ["--alert_type"],
        'help': "<optional for create> The thing to count a quantity of in relation to relation. Required for Alerts. (huh?)"
    },
    "alert_threshold": { 
        'flags': ["--alert_threshold"],
        'help': "<optional for create> The quantity of counttype must exceed in relation to relation. Required for Alerts. (huh?)"
    },
    "alert_comparator": { 
        'flags': ["--alert_comparator"],
        'help': "<optional for create> The relation the count type has to the quantity. Required for Alerts. (huh?)"
    },
    "actions": { 
        'flags': ["--actions"],
        'help': "<optional for create> A list of the actions to fire on alert; supported values are {(email, rss) | script}. For example, actions = rss,email would enable both RSS feed and email sending. Or if you want to just fire a script: actions = script"
    },
    "action.<action_type>.<custom_key>.": { 
        'flags': ["--action.<action_type>.<custom_key>"],
        'help': "<optional for create> A key/value pair that is specific to the action_type. For example, if actions contains email, then the following keys would be necessary: action.email.to=foo@splunk.com  and action.email.sender=splunkbot. For scripts: action.script.filename=doodle.py (note: script is run from $SPLUNK_HOME/bin/scripts/)"
    },
    "dispatch.ttl": { 
        'flags': ["--dispatch.ttl"],
        'help': "<optional for create> The TTL of the search job created"
    },
    "dispatch.buckets": { 
        'flags': ["--dispatch.buckets"],
        'help': "<optional for create> The number of event buckets (huh?)"
    },
    "dispatch.max_count": { 
        'flags': ["--dispatch.max_count"],
        'help': "<optional for create> Maximum number of results"
    },
    "dispatch.max_time": { 
        'flags': ["--dispatch.max_time"],
        'help': "<optional for create> Maximum amount of time in seconds before finalizing the search"
    },
    "dispatch.lookups": { 
        'flags': ["--dispatch.lookups"],
        'help': "<optional for create> Boolean flag indicating whether to enable lookups in this search"
    },
    "dispatch.spawn_process": { 
        'flags': ["--dispatch.spawn_process"],
        'help': "<optional for create> Boolean flag whether to spawn the search as a separate process"
    },
    "dispatch.time_format": { 
        'flags': ["--dispatch.time_format"],
        'help': "<optional for create> Format string for earliest/latest times"
    },
    "dispatch.earliest_time": { 
        'flags': ["--dispatch.earliest_time"],
        'help': "<optional for create> The earliest time for the search"
    },
    "dispatch.latest_time": { 
        'flags': ["--dispatch.latest_time"],
        'help': "<optional for create> The latest time for the search"
    },
    "alert.expires": { 
        'flags': ["--alert.expires"],
        'help': "<optional for create> [time-specifier] The period of time for which the alert will be shown in the alert's dashboard"
    },
    "alert.severity": { 
        'flags': ["--alert.severity"],
        'help': "<optional for create> [int] Specifies the alert severity level, valid values are: 1-debug, 2-info, 3-warn, 4-error, 5-severe, 6-fatal"
    },
    "alert.supress": { 
        'flags': ["--alert.supress"],
        'help': "<optional for create> [bool]whether alert suppression is enabled for this scheduled search"
    },
    "alert.supress_keys": { 
        'flags': ["--alert.supress_keys"],
        'help': "<optional for create> [string] comma delimited list of keys to use for suppress, to access result values use result.<field-name> syntax"
    },
    "alert.supress.period": { 
        'flags': ["--alert.supress.period"],
        'help': "<optional for create> [time-specifier] suppression period, use ack to suppress until acknowledgment is received"
    },
    "alert.digest": { 
        'flags': ["--alert.digest"],
        'help': "<optional for create> [bool] whether the alert actions are executed on the entire result set or on each individual result (defaults to true)"
    },
    "output_mode": { 
        'flags': ["--output_mode"],
        'help': "<optional for all> type of output (atom, xml)"
    },
    ##
    ## special -- catch these options pre-build to perform catch post/get/delete
    ##
    "operation": { 
        'flags': ["--operation"],
        'help': "<optional for create> type of splunk operation: list-all, list, create, delete (defaults to list-all)"
    }
} 

def main(argv):
    """ main entry """
    usage = 'usage: %prog --help for options'
    opts = utils.parse(argv, RULES, ".splunkrc", usage=usage)

    context = binding.connect(**opts.kwargs)
    operation = None

    # splunk.binding.debug = True # for verbose information (helpful for debugging)

    # Extract from command line and build into variable args
    kwargs = {}
    for key in RULES.keys():
        if opts.kwargs.has_key(key):
            if key == "operation":
                operation = opts.kwargs[key]
            else:
                kwargs[key] = opts.kwargs[key]

    # no operation? if name present, default to list, otherwise list-all
    if not operation:
        if kwargs.has_key('name'):
            operation = 'list'
        else:
            operation = 'list-all'
    
    # pre-sanitize
    if (operation != "list" and operation != "create" 
                            and operation != "delete"
                            and operation != "list-all"):
        print "operation %s not one of list-all, list, create, delete" % operation
        sys.exit(0)

    if not kwargs.has_key('name') and operation != "list-all":
        print "operation requires a name"
        sys.exit(0)

    # remove arg 'name' from passing through to operation builder, except on create
    if operation != "create" and operation != "list-all":
        name = kwargs['name']
        kwargs.pop('name')

    # perform operation on saved search created with args from cli
    if operation == "list-all":
        result = context.get("saved/searches",  **kwargs)
    elif operation == "list":
        result = context.get("saved/searches/%s" % name, **kwargs)
    elif operation == "create":
        result = context.post("saved/searches", **kwargs)
    else:
        result = context.delete("saved/searches/%s" % name, **kwargs)
    print "HTTP STATUS: %d" % result.status
    xml_data = result.body.read()
    sys.stdout.write(xml_data)

if __name__ == "__main__":
    main(sys.argv[1:])
