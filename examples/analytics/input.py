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

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from datetime import datetime
import splunklib.client as client

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

__all__ = [
    "AnalyticsTracker",
]

ANALYTICS_INDEX_NAME = "sample_analytics"
ANALYTICS_SOURCETYPE = "sample_analytics"
APPLICATION_KEY = "application"
EVENT_KEY = "event"
DISTINCT_KEY = "distinct_id"
EVENT_TERMINATOR = "\\r\\n-----end-event-----\\r\\n"
PROPERTY_PREFIX = "analytics_prop__"

class AnalyticsTracker:
    def __init__(self, application_name, splunk_info, index = ANALYTICS_INDEX_NAME):
        self.application_name = application_name
        self.splunk = client.connect(**splunk_info)
        self.index = index

        if not self.index in self.splunk.indexes:
            self.splunk.indexes.create(self.index)
        assert(self.index in self.splunk.indexes)

        if ANALYTICS_SOURCETYPE not in self.splunk.confs['props']:
            self.splunk.confs["props"].create(ANALYTICS_SOURCETYPE)
            stanza = self.splunk.confs["props"][ANALYTICS_SOURCETYPE]
            stanza.submit({
                "LINE_BREAKER": "(%s)" % EVENT_TERMINATOR,
                "CHARSET": "UTF-8",
                "SHOULD_LINEMERGE": "false"
            })
        assert(ANALYTICS_SOURCETYPE in self.splunk.confs['props'])

    @staticmethod
    def encode(props):
        encoded = " "
        for k,v in props.iteritems():
            # We disallow dictionaries - it doesn't quite make sense.
            assert(not isinstance(v, dict))

            # We do not allow lists
            assert(not isinstance(v, list))

            # This is a hack to escape quotes
            if isinstance(v, str):
                v = v.replace('"', "'")

            encoded += ('%s%s="%s" ' % (PROPERTY_PREFIX, k, v))

        return encoded

    def track(self, event_name, time = None, distinct_id = None, **props):
        if time is None:
            time = datetime.now().isoformat()
            
        event = '%s %s="%s" %s="%s" ' % (
            time,
            APPLICATION_KEY, self.application_name, 
            EVENT_KEY, event_name)

        assert(not APPLICATION_KEY in props.keys())
        assert(not EVENT_KEY in props.keys())

        if distinct_id is not None:
            event += ('%s="%s" ' % (DISTINCT_KEY, distinct_id))
            assert(not DISTINCT_KEY in props.keys())

        event += AnalyticsTracker.encode(props)

        self.splunk.indexes[self.index].submit(event, sourcetype=ANALYTICS_SOURCETYPE)

def main():
    usage = ""

    argv = sys.argv[1:]

    splunk_opts = utils.parse(argv, {}, ".splunkrc", usage=usage)
    tracker = AnalyticsTracker("cli_app", splunk_opts.kwargs)
    
    #tracker.track("test_event", "abc123", foo="bar", bar="foo")

if __name__ == "__main__":
    main()
