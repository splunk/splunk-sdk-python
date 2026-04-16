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

from dataclasses import dataclass
from typing import Any, Mapping

import httpx


@dataclass(frozen=True)
class PredefinedModel:
    """Base class for models that are predefined in the SDK"""

    model: str


@dataclass(frozen=True)
class OpenAIModel(PredefinedModel):
    """Predefined OpenAI Model"""

    model: str
    base_url: str
    api_key: str
    temperature: float | None = None

    extra_body: Mapping[str, Any] | None = None
    """
    Optional additional properties to include in the request parameters when
    making requests to OpenAI compatible APIs.

    This is the recommended way to pass custom parameters that are specific to your
    OpenAI-compatible API provider but not part of the standard OpenAI API.
    """

    httpx_client: httpx.AsyncClient | None = None
    """
    Optional http client, that is used for all outgoing HTTP requests.

    Can be leveraged to set custom Auth headers to OpenAI compatible APIs:

        httpx_client=httpx.AsyncClient(auth=auth_handler)
    """


@dataclass(frozen=True)
class AnthropicModel(PredefinedModel):
    """Predefined Anthropic Model"""

    model: str
    api_key: str
    base_url: str
    temperature: float | None = None


__all__ = [
    "AnthropicModel",
    "OpenAIModel",
    "PredefinedModel",
]
