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
import splunklib

from tests import testlib
from splunklib.wire._internal import Telemetry, EventTelemetryMetric, AggregateTelemetryMetric

@pytest.mark.app
class TestTelemetry(testlib.SDKTestCase):
    def setUp(self):
        super(TestTelemetry, self).setUp()

        self.service.namespace['owner'] = 'nobody'
        self.service.namespace['app'] = 'sdk-app-collection'

        self.telemetry = Telemetry(self.service)

    def test_submit(self):
        # create a telemetry metric
        metric = EventTelemetryMetric(**{
            'component': 'telemetry_test_case',
            'data': {
                 'version': splunklib.__version__,
                 'source': 'splunk-sdk-python/mod-inputs'
            }
        })

        # call out to telemetry
        response, _body = self.telemetry.submit(metric.to_wire())

        # it should return a 201
        self.assertEqual(response.status, 201)

    def test_event_submit(self):
        # create a telemetry metric
        metric = EventTelemetryMetric(**{
            'component': 'telemetry_test_case',
            'data': {
                 'version': splunklib.__version__,
                 'source': 'splunk-sdk-python/mod-inputs'
            },
            'version': 'test',
            'index_data': False,
            'timestamp': 0,
            'visibility': ['anonymous'],
        })

        # call out to telemetry
        response, _body = self.telemetry.submit(metric.to_wire())

        # it should return a 201
        self.assertEqual(response.status, 201)

    def test_aggregate_submit(self):
        # create a telemetry metric
        metric = AggregateTelemetryMetric(**{
            'component': 'telemetry_test_case',
            'data': {
                 'version': splunklib.__version__,
                 'source': 'splunk-sdk-python/mod-inputs'
            },
            'version': 'test',
            'index_data': False,
            'timestamp': 3,
            'visibility': ['anonymous'],
            'begin': 0,
            'end': 1,
        })

        # call out to telemetry
        response, _body = self.telemetry.submit(metric.to_wire())

        # it should return a 201
        self.assertEqual(response.status, 201)
