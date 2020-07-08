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

class EventTelemetryMetric(TelemetryMetric):
    METRIC_TYPE = 'event'

    def __init__(self, component, data,
                 opt_in_required=2,
                 version=None,
                 timestamp=None,
                 visibility=None,
                 index_data=None,
                 user_id=None,
                 experience_id=None):
        super(EventTelemetryMetric, self).__init__(
            EventTelemetryMetric.METRIC_TYPE,
            component,
            data,
            opt_in_required=opt_in_required,
            version=version,
            timestamp=timestamp,
            visibility=visibility,
            index_data=index_data
        )

        self.user_id = user_id
        self.experience_id = experience_id

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def experience_id(self):
        return self._experience_id

    @experience_id.setter
    def experience_id(self, value):
        self._experience_id = value

    def to_wire(self):
        wire = super(EventTelemetryMetric, self).to_wire()

        if self.user_id is not None:
            wire['userID'] = self.user_id

        if self.experience_id is not None:
            wire['experienceID'] = self.experience_id

        return wire
