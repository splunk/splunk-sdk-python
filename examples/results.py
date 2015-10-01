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

"""A script that reads XML search results from stdin and pretty-prints them
   back to stdout. The script is designed to be used with the search.py 
   example, eg: './search.py "search 404" | ./results.py'"""
 
from pprint import pprint
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import splunklib.results as results

def pretty():
    reader = results.ResultsReader(sys.stdin)
    for event in reader:
        pprint(event)

if __name__ == "__main__":
    pretty()
