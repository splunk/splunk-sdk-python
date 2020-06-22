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

import json

from splunklib.client import Entity

class JsonSink(Entity):
    """This class represents a JSON-based write-only sink of entities in the Splunk
    instance, notably telemetry-metric.
    """
    JSON_HEADER = [('Content-Type', 'application/json')]

    def __init__(self, service, path, **kwargs):
        super(JsonSink, self).__init__(service, path, skip_refresh=True, **kwargs)

    def _post(self, url, **kwargs):
        owner, app, sharing = self._proper_namespace()

        return self.service.post(self.path + url, owner=owner, app=app, sharing=sharing, **kwargs)

    def submit(self, data):
        """
        Submits an item to the sink.

        :param data: data to submit
        :type data: ``dict``

        :return: return data
        :rtype: ``dict``
        """

        response = self._post('', headers=self.__class__.JSON_HEADER, body=json.dumps(data))
        body = json.loads(response.body.read().decode('utf-8'))

        return response, body
