# Copyright © 2011-2026 Splunk, Inc.
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

import os
import sys
from urllib import parse

sys.path.insert(0, "/splunklib-deps")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from splunklib.modularinput import Argument, Event, Scheme, Script


class ModularInput(Script):
    """
    This app provides an example of a modular input that
    can be used in Settings => Data inputs => Local inputs => modularinput
    """

    endpoint_arg = "endpoint"

    def get_scheme(self):
        scheme = Scheme("modularinput")

        scheme.use_external_validation = True
        scheme.use_single_instance = True

        endpoint = Argument(self.endpoint_arg)
        endpoint.title = "URL"
        endpoint.data_type = Argument.data_type_string
        endpoint.description = "URL"
        endpoint.required_on_create = True
        scheme.add_argument(endpoint)

        return scheme

    def validate_input(self, definition):
        self.check_service_access()

        url = definition.parameters[self.endpoint_arg]
        parsed = parse.urlparse(url)
        if parsed.scheme != "https":
            raise ValueError(f"non-supported scheme {parsed.scheme}")

    def stream_events(self, inputs, ew):
        self.check_service_access()

        for input_name, input_item in list(inputs.inputs.items()):
            event = Event()
            event.stanza = input_name
            event.data = "example message"
            ew.write_event(event)

    def check_service_access(self):
        # Both validate_input and stream_events should have access to the Splunk
        # instance that executed the modular input.
        if self.service is None:
            raise Exception("self.Service == None")
        self.service.info  # make sure that we are properly authenticated and self.service works


if __name__ == "__main__":
    sys.exit(ModularInput().run(sys.argv))
