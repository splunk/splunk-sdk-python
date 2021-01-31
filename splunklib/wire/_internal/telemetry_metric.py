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

class TelemetryMetric:
    def __init__(self, metric_type, component, data, opt_in_required=2):
        self.metric_type = metric_type
        self.component = component
        self.data = data
        self.opt_in_required = opt_in_required

    @property
    def metric_type(self):
        return self._metric_type

    @metric_type.setter
    def metric_type(self, value):
        self._metric_type = value

    @property
    def component(self):
        return self._component

    @component.setter
    def component(self, value):
        self._component = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def opt_in_required(self):
        return self._opt_in_required

    @opt_in_required.setter
    def opt_in_required(self, value):
        self._opt_in_required = value

    def to_wire(self):
        return {
            'type': self.metric_type,
            'component': self.component,
            'data': self.data,
            'optInRequired': self.opt_in_required,
        }
