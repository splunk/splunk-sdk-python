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

"""An example that shows how to use the Splunk binding module to create a
   convenient 'wrapper' interface around the Splunk REST APIs. The example
   binds to a sampling of endpoints showing how to access collections,
   entities and 'method-like' endpoints."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib.binding import connect

try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


class Service:
    def __init__(self, context):
        self.context = context

    def apps(self):
        return self.context.get("apps/local")

    def indexes(self):
        return self.context.get("data/indexes")

    def info(self):
        return self.context.get("/services/server/info")

    def settings(self):
        return self.context.get("/services/server/settings")

    def search(self, query, **kwargs):
        return self.context.post("search/jobs/export", search=query, **kwargs)

def main(argv):
    opts = parse(argv, {}, ".splunkrc")
    context = connect(**opts.kwargs)
    service = Service(context)
    assert service.apps().status == 200
    assert service.indexes().status == 200
    assert service.info().status == 200
    assert service.settings().status == 200
    assert service.search("search 404").status == 200

if __name__ == "__main__":
    main(sys.argv[1:])
