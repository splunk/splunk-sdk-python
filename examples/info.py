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

"""An example that prints Splunk service info & settings."""

import sys

import splunklib.client as client

from utils import parse

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    service = client.connect(**opts.kwargs)

    content = service.info
    for key in sorted(content.keys()):
        value = content[key]
        if isinstance(value, list):
            print "%s:" % key
            for item in value: print "    %s" % item
        else:
            print "%s: %s" % (key, value)

    print "Settings:"
    content = service.settings.content
    for key in sorted(content.keys()):
        value = content[key]
        print "    %s: %s" % (key, value)
