# Copyright © 2011-2025 Splunk, Inc.
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

from typing import Any, Optional, Tuple
from splunklib.data import Record
from splunklib.internal.telemetry.metric import Metric
import json

# TODO: decide: either struggle with the type hints or get rid of them and stick to the convention

CONTENT_TYPE = [('Content-Type', 'application/json')]
DEFAULT_TELEMETRY_USER = "nobody"  # User `nobody` always exists
DEFAULT_TELEMETRY_APP = "splunk_instrumentation"  # This app is shipped with Splunk and has `telemetry-metric` endpoint
TELEMETRY_ENDPOINT = "telemetry-metric"


class TelemetrySender:
    # FIXME: adding Service typehint produces circular dependency
    # service: Service

    def __init__(self, service):
        self.service = service

    def send(self, metric: Metric, user: Optional[str] = None, app: Optional[str] = None) -> Tuple[Record, Any]:
        """Sends the metric to the `telemetry-metric` endpoint.

        :param user: Optional user that sends the telemetry.
        :param app: Optional app that is used to send the telemetry.

        If those values are omitted, the default values are used.
        This makes sure that, even if missing some info, the event will be sent.
        """

        metric_body = self._metric_to_json(metric)

        user = user or DEFAULT_TELEMETRY_USER
        app = app or DEFAULT_TELEMETRY_APP

        response = self.service.post(
            "telemetry-metric",
            user,
            app,
            headers=[('Content-Type', 'application/json')],
            body=metric_body,
        )

        body = json.loads(response.body.read().decode('utf-8'))

        return response, body

    def _metric_to_json(self, metric: Metric) -> str:
        m = {
            "type": metric.type.value,
            "component": metric.component,
            "data": metric.data,
            "optInRequired": metric.opt_in_required
        }

        return json.dumps(m)
