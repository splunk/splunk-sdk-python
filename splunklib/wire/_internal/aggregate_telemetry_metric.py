# coding=utf-8
#
# Copyright © 2011-2020 Splunk, Inc.
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

from splunklib.wire._internal.telemetry_metric import TelemetryMetric

class AggregateTelemetryMetric(TelemetryMetric):
    METRIC_TYPE = 'aggregate'

    def __init__(self, component, data,
                 opt_in_required=2,
                 version=None,
                 timestamp=None,
                 visibility=None,
                 index_data=None,
                 begin=None,
                 end=None):
        super(AggregateTelemetryMetric, self).__init__(
            AggregateTelemetryMetric.METRIC_TYPE,
            component,
            data,
            opt_in_required=opt_in_required,
            version=version,
            timestamp=timestamp,
            visibility=visibility,
            index_data=index_data
        )

        self.begin = begin
        self.end = end

    @property
    def begin(self):
        return self._begin

    @begin.setter
    def begin(self, value):
        self._begin = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    def to_wire(self):
        wire = super(AggregateTelemetryMetric, self).to_wire()

        if self.begin is not None:
            wire['begin'] = self.begin

        if self.end is not None:
            wire['end'] = self.end

        return wire
