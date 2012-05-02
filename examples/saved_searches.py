#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

"""A command line utility that lists saved searches."""

import sys
sys.path.insert(0, '../')

from splunklib.client import connect

from utils import parse

def main():
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    service = connect(**opts.kwargs)

    for saved_search in service.saved_searches:
        header = saved_search.name
        print header
        print '='*len(header)
        content = saved_search.content
        for key in sorted(content.keys()):
            value = content[key]
            print "%s: %s" % (key, value)
        history = saved_search.history()
        if len(history) > 0:
            print "history:"
            for job in history:
                print "    %s" % job.name
        print

if __name__ == "__main__":
    main()


