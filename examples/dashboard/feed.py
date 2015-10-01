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
#
# This example shows how to integrate Splunk with 3rd party services using
# the Python SDK. In this case, we use Twitter data and Leftronic 
# (http://www.leftronic.com) dashboards. You can find more information
# in the README.


import sys, os, urllib2, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from xml.etree import ElementTree

import splunklib.client as client
import splunklib.results as results
try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


leftronic_access_key = ""

def send_data(access_key, stream_name, point = None, command = None):
    data = {
        "accessKey": access_key,
        "streamName": stream_name
    }
    
    if not point is None:
        data["point"] = point
    if not command is None:
        data["command"] = command   

    request = urllib2.Request("https://www.leftronic.com/customSend/",
        data = json.dumps(data)
    )
    response = urllib2.urlopen(request)


def top_sources(service):
    query = "search index=twitter status_source=* | stats count(status_source) as count by status_source | sort -count | head 5"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        data = []

        for result in reader:
            if isinstance(result, dict):
                status_source_xml = result["status_source"].strip()
                source = status_source_xml
                if status_source_xml.startswith("<a"):
                    try:
                        source = ElementTree.XML(status_source_xml).text
                    except Exception, e:
                        print status_source_xml
                        raise e
                
                data.append({
                    "name": source,
                    "value": int(result["count"])
                })

        send_data(access_key = leftronic_access_key, stream_name = "top_sources", point = { "leaderboard": data })

    return created_job, lambda job: iterate(job)

def geo(service):
    query = "search index=twitter coordinates_type=Point coordinates_coordinates=* | fields coordinates_coordinates"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        points = []
        for result in reader:
            if isinstance(result, dict):
                lng, lat = result["coordinates_coordinates"].split(",")
                point = {
                    "latitude": lat,
                    "longitude": lng,
                }
                points.append(point)

                
        send_data(access_key = leftronic_access_key, stream_name = "geo", command = "clear")
        send_data(access_key = leftronic_access_key, stream_name = "geo", point = points)

    return created_job, lambda job: iterate(job)

def tweets(service):
    query = "search index=twitter | head 15 | fields user_name, user_screen_name, text, user_profile_image_url "
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        for result in reader:
            if isinstance(result, dict):
                user = result.get("user_name", result.get("user_screen_name", ""))
                text = result.get("text", "")
                img = result.get("user_profile_image_url", "")
                point = {
                    "title": user,
                    "msg": text,
                    "imgUrl": img
                }
                
                send_data(access_key = leftronic_access_key, stream_name = "tweets", point = point)
    
    return created_job, lambda job: iterate(job)

def counts(service):    
    query = "search index=twitter | stats count by user_id | fields user_id, count | stats count(user_id) as user_count, sum(count) as tweet_count"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        for result in reader:
            if isinstance(result, dict):
                user_count = result["user_count"]
                tweet_count = result.get("tweet_count", 0)

                # Send user count
                point = int(user_count)
                send_data(access_key = leftronic_access_key, stream_name = "users_count_5m", point = point)

                # Send tweet count
                point = int(tweet_count)
                send_data(access_key = leftronic_access_key, stream_name = "tweets_count_5m", point = point)

    return created_job, lambda job: iterate(job)

def top_tags(service):
    query = 'search index=twitter text=* | rex field=text max_match=1000 "#(?<tag>\w{1,})" | fields tag | mvexpand tag | top 5 tag'
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        data = []

        for result in reader:
            if isinstance(result, dict):
                tag = result["tag"]
                count = result["count"]

                data.append({
                    "name": tag,
                    "value": int(count)
                })

        send_data(access_key = leftronic_access_key, stream_name = "top_tags", point = { "leaderboard": data })
    
    return created_job, lambda job: iterate(job)

def main(argv):
    # Parse the command line args.
    opts = parse(argv, {}, ".splunkrc")

    # Connect to Splunk
    service = client.connect(**opts.kwargs)
    
    # This is the list of dashboard streams
    streams = [
        top_sources,
        geo,
        tweets,
        counts,
        top_tags,
    ]

    jobs = []
    iterators = []

    # For each stream, we get back the created job
    # that feeds the stream, and also the iterator
    # that will poll the job and forward the data
    # to the dashboard
    for stream in streams:
        job, iterator = stream(service)
        jobs.append(job)
        iterators.append(iterator)

    try:
        while True:
            # For each (job,iterator) pair, we invoke the
            # iterator, which in turn will pull new results
            # from that job, and send them up to the dashboard
            for job, iterator in zip(jobs, iterators):
                iterator(job)
                
    except KeyboardInterrupt:
        pass
    finally:
        for job in jobs:
            job.cancel()
if __name__ == "__main__":
    main(sys.argv)

    
