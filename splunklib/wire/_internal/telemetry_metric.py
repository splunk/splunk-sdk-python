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

from abc import ABCMeta
from splunklib import six

class TelemetryMetric(six.with_metaclass(ABCMeta, object)):
    def __init__(self, metric_type, component, data,
                 opt_in_required=2,
                 version=None,
                 index_data=None,
                 timestamp=None,
                 visibility=None):
        self.metric_type = metric_type
        self.component = component
        self.data = data
        self.opt_in_required = opt_in_required
        self.version = version
        self.index_data = index_data
        self.timestamp = timestamp
        self.visibility = visibility

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

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def index_data(self):
        return self._index_data

    @index_data.setter
    def index_data(self, value):
        self._index_data = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        self._visibility = value

    def to_wire(self):
        wire = {
            'type': self.metric_type,
            'component': self.component,
            'data': self.data,
            'optInRequired': self.opt_in_required,
        }

        if self.version is not None:
            wire['version'] = self.version

        if self.index_data is not None:
            wire['indexData'] = self.index_data

        if self.timestamp is not None:
            wire['timestamp'] = self.timestamp

        if self.visibility is not None:
            wire['visibility'] = self.visibility

        return wire
