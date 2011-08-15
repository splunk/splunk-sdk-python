#!/usr/bin/env python
#
# Copyright 2011 Splunk, Inc.
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


import sys, datetime, urllib2, json
from xml.etree import ElementTree

import splunk.client
import splunk.results as results
from utils import parse, error

leftronic_access_key = ""

def send_data(access_key, stream_name, point):
    data = {
        "accessKey": access_key,
        "streamName": stream_name,
        "point": point,
    }

    request = urllib2.Request("https://beta.leftronic.com/customSend/",
        data = json.dumps(data)
    )
    response = urllib2.urlopen(request)


def top_sources(service):
    query = "search index=twitter status_source=* | stats count(status_source) as count by status_source | sort -count | head 5"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        data = []

        for kind,result in reader:
            if kind == results.RESULT:
                status_source_xml = result["status_source"].strip()
                source = status_source_xml
                if (status_source_xml.startswith("<a")):
                    try:
                        source = ElementTree.XML(status_source_xml).text
                    except:
                        print status_source_xml
                        raise e
                
                data.append({
                    "name": source,
                    "value": int(result["count"])
                })

        send_data(access_key = leftronic_access_key, stream_name = "top_sources", point = { "leaderboard": data })

    return (created_job, lambda job: iterate(job))

def geo(service):
    query = "search index=twitter coordinates_type=Point coordinates_coordinates=* | fields coordinates_coordinates"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        for kind,result in reader:
            if kind == results.RESULT:
                lng, lat = result["coordinates_coordinates"].split(",")
                point = {
                    "latitude": lat,
                    "longitude": lng,
                }

                send_data(access_key = leftronic_access_key, stream_name = "geo", point = point)

    return (created_job, lambda job: iterate(job))

def tweets(service):
    query = "search index=twitter | head 15 | fields user_name, user_screen_name, text, user_profile_image_url "
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        for kind,result in reader:
            if kind == results.RESULT:
                user = result.get("user_name", result.get("user_screen_name", ""))
                text = result.get("text", "")
                img = result.get("user_profile_image_url", "")
                point = {
                    "title": user,
                    "msg": text,
                    "imgUrl": img
                }
                
                send_data(access_key = leftronic_access_key, stream_name = "tweets", point = point)
    
    return (created_job, lambda job: iterate(job))

def counts(service):    
    query = "search index=twitter | stats count by user_id | fields user_id, count | stats count(user_id) as user_count, sum(count) as tweet_count"
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        for kind,result in reader:
            if kind == results.RESULT:
                user_count = result["user_count"]
                tweet_count = result.get("tweet_count", 0)

                # Send user count
                point = int(user_count)
                send_data(access_key = leftronic_access_key, stream_name = "users_count_5m", point = point)

                # Send tweet count
                point = int(tweet_count)
                send_data(access_key = leftronic_access_key, stream_name = "tweets_count_5m", point = point)

    return (created_job, lambda job: iterate(job))

def top_tags(service):
    query = 'search index=twitter text=* | rex field=text max_match=1000 "#(?<tag>\w{1,})" | fields tag | mvexpand tag | top 5 tag'
    created_job = service.jobs.create(query, search_mode="realtime", earliest_time="rt-5m", latest_time="rt")

    def iterate(job):
        reader = results.ResultsReader(job.preview())
        data = []

        for kind,result in reader:
            if kind == results.RESULT:
                tag = result["tag"]
                count = result["count"]

                data.append({
                    "name": tag,
                    "value": int(count)
                })

        send_data(access_key = leftronic_access_key, stream_name = "top_tags", point = { "leaderboard": data })
    
    return (created_job, lambda job: iterate(job))

def main(argv):
    global urllib2
    usage = "async.py <sync | async>"

    # Parse the command line args.
    opts = parse(argv, {}, ".splunkrc")

    # Connect to Splunk
    service = splunk.client.connect(**opts.kwargs)
    
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

    
