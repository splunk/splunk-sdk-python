#
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

sys.path.insert(0, "/splunklib-deps")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from splunklib.ai.registry import ToolContext, ToolRegistry

registry = ToolRegistry()


@registry.tool(description="Returns the current temperature in the city")
def temperature(ctx: ToolContext, city: str) -> str:
    # Make sure we can access the Splunk API.
    ctx.service.info.startup_time

    if city == "Krakow":
        return "31.5C"
    else:
        return "22.1C"


registry.run()
