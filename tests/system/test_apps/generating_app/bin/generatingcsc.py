#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2024 Splunk, Inc.
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

import os, sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import (
    dispatch,
    GeneratingCommand,
    Configuration,
    Option,
    validators,
)


@Configuration()
class GeneratingCSC(GeneratingCommand):
    """
    The generatingapp command generates a specific number of records.

    Example:

    ``| generatingcsc count=4``

    Returns a 4 records having text 'Test Event'.
    """

    count = Option(require=True, validate=validators.Integer(0))

    def generate(self):
        self.logger.debug("Generating %s events" % self.count)
        for i in range(1, self.count + 1):
            text = f"Test Event {i}"
            yield {"_time": time.time(), "event_no": i, "_raw": text}


dispatch(GeneratingCSC, sys.argv, sys.stdin, sys.stdout, __name__)
