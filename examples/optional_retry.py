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

"""A command line utility that shows how to use the optional retries parameters, "retries" defines the number of time
an API call should be retried before erroring out and "retryBackoff" defines the time to wait in-between the API
retry calls default value is 10 seconds.The example is shown using the "services" API to get list of the services
after a splunk restart, API call will normally fail while Splunk in restart mode but with "retries" set it will
prevent the error out """

from __future__ import absolute_import
from __future__ import print_function
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib.client import connect

try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


def main():
    opts = parse([], {}, ".env")
    kwargs = opts.kwargs.copy()
    kwargs.update({'retries': 5, 'retryBackoff': 5})
    service = connect(**kwargs)
    service.restart(timeout=10)
    print(service.get("/services"))


if __name__ == "__main__":
    main()
