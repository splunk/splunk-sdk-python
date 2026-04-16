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

import splunk  # pyright: ignore[reportMissingImports]

# Simple handler, that return 200 when the /splunk-mcp-server.tgz exists
# on the splunk instance.
# Used by ../../../test_ai_agentic_test_app.py to determine whether the
# Splunk MCP Server is available on the splunk instance to be installed.


class Handler(splunk.rest.BaseRestHandler):  # pyright: ignore[reportUntypedBaseClass]
    def handle_GET(self) -> None:
        if os.path.exists("/splunk-mcp-server.tgz"):
            self.response.setStatus(200)
        else:
            self.response.setStatus(404)
