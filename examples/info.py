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

"""An example that prints Splunk service info & settings."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import splunklib.client as client

try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

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
