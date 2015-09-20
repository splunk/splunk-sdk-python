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

from bottle import route, run, debug, template, static_file, request

from time import strptime, mktime

from input import AnalyticsTracker
from output import AnalyticsRetriever, TimeRange
try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

splunk_opts = None
retrievers = {}

def get_retriever(name):
    global retrievers
    retriever = None
    if retrievers.has_key(name):
        retriever = retrievers[name]
    else:
        retriever = AnalyticsRetriever(name, splunk_opts)
        retrievers[name] = retriever

    return retriever

@route('/static/:file#.+#')
def help(file):
    raise static_file(file, root='.')

@route('/applications')
def applications():
    tracker.track("list_applications")

    retriever = get_retriever("")
    applications = retriever.applications()
    
    output = template('templates/applications', applications=applications)
    return output

def track_app_detail(event, event_name, prop_name, time_range = None):
    properties = {}
    if event_name is not None and not event_name == "":  
        properties["ev_name"] = event_name
    if prop_name is not None and not prop_name == "": 
        properties["prop_name"] = prop_name
    if time_range is not None and not time_range == "": 
        properties["time_range"] = time_range

    tracker.track(event, **properties)

@route('/api/application/:name')
def application(name):
    retriever = get_retriever(name)
    event_name = request.GET.get("event_name", "")
    property_name = request.GET.get("property", "")
    time_range = request.GET.get("time_range", TimeRange.MONTH)

    # Track the event
    track_app_detail("api_app_details", event_name, property_name, time_range = time_range)

    events = retriever.events()

    events_over_time = retriever.events_over_time(event_name=event_name, property=property_name, time_range=time_range) 
    properties = []
    if event_name:
        properties = retriever.properties(event_name)

    # We need to format the events to something the graphing library can handle
    data = []
    for name, ticks in events_over_time.iteritems():
        # We ignore the cases
        if name == "VALUE" or name == "NULL":
            continue

        event_ticks = []
        for tick in ticks:
            time = strptime(tick["time"][:-6] ,'%Y-%m-%dT%H:%M:%S.%f')
            count = tick["count"]
            event_ticks.append([int(mktime(time)*1000),count])
        
        data.append({
            "label": name,
            "data": event_ticks,
        })

    result = {    
        "events": events,
        "event_name": event_name,
        "application_name": retriever.application_name, 
        "properties": properties,
        "data": data,
        "property_name": property_name,
    }

    return result

@route('/application/:name')
def application(name):
    retriever = get_retriever(name)
    event_name = request.GET.get("event_name", "")
    property_name = request.GET.get("property", "")

    # Track the event
    track_app_detail("app_details", event_name, property_name)

    events = retriever.events()

    events_over_time = retriever.events_over_time(event_name=event_name, property=property_name) 
    properties = []
    if event_name:
        properties = retriever.properties(event_name)

    output = template('templates/application', 
                events=events,
                event_name=event_name,
                application_name=retriever.application_name, 
                properties=properties,
                property_name=property_name,
                open_tag="{{",
                close_tag="}}")

    return output

def main():
    argv = sys.argv[1:]

    opts = utils.parse(argv, {}, ".splunkrc")
    global splunk_opts
    splunk_opts = opts.kwargs

    global tracker
    tracker = AnalyticsTracker("analytics", splunk_opts)

    debug(True)
    run(reloader=True)

if __name__ == "__main__":
    main()
