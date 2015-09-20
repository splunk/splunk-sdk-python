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
import splunklib.client as client
import splunklib.results as results
try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

__all__ = [
    "TimeRange",
    "AnalyticsRetriever"
]

ANALYTICS_INDEX_NAME = "sample_analytics"
ANALYTICS_SOURCETYPE = "sample_analytics"
APPLICATION_KEY = "application"
EVENT_KEY = "event"
DISTINCT_KEY = "distinct_id"
EVENT_TERMINATOR = "\\r\\n-----end-event-----\\r\\n"
PROPERTY_PREFIX = "analytics_prop__"

class TimeRange:
    DAY="1d"
    WEEK="1w"
    MONTH="1mon"    

def counts(job, result_key):
    applications = []
    reader = results.ResultsReader(job.results())
    for result in reader:
        if isinstance(result, dict):
            applications.append({
                    "name": result[result_key],
                    "count": int(result["count"] or 0)
                    })
    return applications
    

class AnalyticsRetriever:
    def __init__(self, application_name, splunk_info, index = ANALYTICS_INDEX_NAME):
        self.application_name = application_name
        self.splunk = client.connect(**splunk_info)
        self.index = index

    def applications(self):
        query = "search index=%s | stats count by application" % (self.index)
        job = self.splunk.jobs.create(query, exec_mode="blocking")
        return counts(job, "application")

    def events(self):
        query = "search index=%s application=%s | stats count by event" % (self.index, self.application_name)
        job = self.splunk.jobs.create(query, exec_mode="blocking")
        return counts(job, "event")

    def properties(self, event_name):
        query = 'search index=%s application=%s event="%s" | stats dc(%s*) as *' % (
            self.index, self.application_name, event_name, PROPERTY_PREFIX
        )
        job = self.splunk.jobs.create(query, exec_mode="blocking")

        properties = []
        reader = results.ResultsReader(job.results())
        for result in reader:
            if not isinstance(result, dict):
                continue
            for field, count in result.iteritems():
                # Ignore internal ResultsReader properties
                if field.startswith("$"):
                    continue

                properties.append({
                        "name": field,
                        "count": int(count or 0)
                        })

        return properties

    def property_values(self, event_name, property):
        query = 'search index=%s application=%s event="%s" | stats count by %s | rename %s as %s' % (
            self.index, self.application_name, event_name, 
            PROPERTY_PREFIX + property,
            PROPERTY_PREFIX + property, property
        )
        job = self.splunk.jobs.create(query, exec_mode="blocking")

        values = []
        reader = results.ResultsReader(job.results())
        for result in reader:
            if isinstance(result, dict):
                if result[property]:
                    values.append({
                        "name": result[property],
                        "count": int(result["count"] or 0)
                    })

        return values

    def events_over_time(self, event_name = "", time_range = TimeRange.MONTH, property = ""):
        query = 'search index=%s application=%s event="%s" | timechart span=%s count by %s | fields - _span*' % (
            self.index, self.application_name, (event_name or "*"), 
            time_range,
            (PROPERTY_PREFIX + property) if property else "event",
        )
        job = self.splunk.jobs.create(query, exec_mode="blocking")

        over_time = {}
        reader = results.ResultsReader(job.results())
        for result in reader:
            if isinstance(result, dict):
                # Get the time for this entry
                time = result["_time"]
                del result["_time"]

                # The rest is in the form of [event/property]:count
                # pairs, so we decode those
                for key,count in result.iteritems():
                    # Ignore internal ResultsReader properties
                    if key.startswith("$"):
                        continue

                    entry = over_time.get(key, [])
                    entry.append({
                        "count": int(count or 0),
                        "time": time,
                    })
                    over_time[key] = entry

        return over_time

def main():
    usage = ""

    argv = sys.argv[1:]

    opts = utils.parse(argv, {}, ".splunkrc", usage=usage)
    retriever = AnalyticsRetriever(opts.args[0], opts.kwargs)    

    #events = retriever.events()
    #print events
    #for event in events:
    #    print retriever.properties(event["name"])

    #print retriever.property_values("critical", "version")
    #print retriever.events_over_time(time_range = TimeRange.MONTH)
    #print retriever.applications()
    #print retriever.events_over_time()

if __name__ == "__main__":
    main()
