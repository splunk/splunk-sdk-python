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

"""Follows (aka tails) a realtime search using the job endpoints and prints
   results to stdout."""

from pprint import pprint
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import time

import splunklib.client as client
import splunklib.results as results

try:
    import utils
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

def follow(job, count, items):
    offset = 0 # High-water mark
    while True:
        total = count()
        if total <= offset:
            time.sleep(1) # Wait for something to show up
            job.refresh()
            continue
        stream = items(offset+1)
        for event in results.ResultsReader(stream):
            pprint(event)
        offset = total

def main():
    usage = "usage: follow.py <search>"
    opts = utils.parse(sys.argv[1:], {}, ".splunkrc", usage=usage)

    if len(opts.args) != 1:
        utils.error("Search expression required", 2)
    search = opts.args[0]

    service = client.connect(**opts.kwargs)

    job = service.jobs.create(
        search, 
        earliest_time="rt", 
        latest_time="rt", 
        search_mode="realtime")

    # Wait for the job to transition out of QUEUED and PARSING so that
    # we can if its a transforming search, or not.
    while True:
        job.refresh()
        if job['dispatchState'] not in ['QUEUED', 'PARSING']:
            break
        time.sleep(2) # Wait
        
    if job['reportSearch'] is not None: # Is it a transforming search?
        count = lambda: int(job['numPreviews'])
        items = lambda _: job.preview()
    else:
        count = lambda: int(job['eventCount'])
        items = lambda offset: job.events(offset=offset)
    
    try:
        follow(job, count, items)
    except KeyboardInterrupt:
        print "\nInterrupted."
    finally:
        job.cancel()
    
if __name__ == "__main__":
    main()

