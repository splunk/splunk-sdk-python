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

import sys

if sys.version_info < (3, 13):
    raise ImportError("Python 3.13 or newer is required to use this module")

from splunklib.ai.agent import Agent
from splunklib.ai.model import AnthropicModel, GoogleModel, OpenAIModel
from splunklib.ai.security import (
    create_structured_prompt,
    detect_injection,
    truncate_input,
)

__all__ = [
    "Agent",
    "AnthropicModel",
    "OpenAIModel",
    "GoogleModel",
    "create_structured_prompt",
    "detect_injection",
    "truncate_input",
]
