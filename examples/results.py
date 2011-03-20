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

"""A script that reads XML search results from stdin and pretty-prints them
   back to stdout. The script is designed to be used with the search.py 
   example, eg: './search.py "search 404" | ./results.py'"""
 
from pprint import pprint
import sys
import time

import splunk.results as results

def pretty():
    reader = results.ResultsReader(sys.stdin)
    while True:
        kind = reader.read()
        if kind == None: break
        if kind == results.RESULT:
            event = reader.value
            pprint(event)

def summary():
    reader = results.ResultsReader(sys.stdin)
    last = None
    count = 0 
    while True:
        kind = reader.read()
        if kind == None: 
            print
            break
        if kind == results.RESULTS:
            if last == results.RESULT: print
            print "# Results: preview = %s" % reader.value['preview']
        elif kind == results.MESSAGE:
            if last == results.RESULT: print
            print "# Messasge: %s" % reader.value['message']
        elif kind == results.RESULT:
            count += 1
            if last != results.RESULT or count % 1 == 0: 
                sys.stdout.write(".")
                sys.stdout.flush()
        last = kind

def timeit():
    start = time.time()
    reader = results.ResultsReader(sys.stdin)
    count = 0
    while True:
        kind = reader.read()
        if kind == None: break
        if kind == results.RESULT: count += 1
    delta = time.time() - start
    print "%d results in %f secs = %f results/sec" % (count, delta, count/delta)

if __name__ == "__main__":
    pretty()
