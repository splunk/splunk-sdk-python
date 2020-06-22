#!/usr/bin/env python
#
# Copyright 2011-2014 Splunk, Inc.
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

from __future__ import absolute_import
import pytest

from tests import testlib
from splunklib.wire._internal.telemetry import Telemetry
from splunklib.wire._internal.telemetry_metric import TelemetryMetric

try:
    import unittest
except ImportError:
    import unittest2 as unittest

@pytest.mark.app
class TelemetryTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(TelemetryTestCase, self).setUp()

        self.service.namespace['owner'] = 'nobody'
        self.service.namespace['app'] = 'sdk-app-collection'

        self.telemetry = Telemetry(self.service)

    def test_submit(self):
        # create a telemetry metric
        metric = TelemetryMetric(**{
            'metric_type': 'event',
            'component': 'telemetry_test_case',
            'data': {
                'testValue': 32
            }
        })

        # call out to telemetry
        response, _body = self.telemetry.submit(metric.to_wire())

        # it should return a 201
        self.assertEqual(response.status, 201)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
