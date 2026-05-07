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

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from google.oauth2 import service_account


@dataclass(frozen=True, kw_only=True)
class PredefinedModel:
    """Base class for models that are predefined in the SDK"""

    model: str


@dataclass(frozen=True, kw_only=True)
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


@dataclass(frozen=True, kw_only=True)
class AnthropicModel(PredefinedModel):
    """Predefined Anthropic Model"""

    model: str
    api_key: str
    base_url: str
    temperature: float | None = None


@dataclass(frozen=True, kw_only=True)
class GoogleModel(PredefinedModel):
    """Predefined Google Model

    Supports the Gemini API and Vertex AI. The backend is chosen
    automatically: Vertex AI when ``project`` or ``credentials`` is set,
    otherwise the Gemini API. Override with ``vertexai=True/False``.

    See the README for full usage examples and authentication options.
    """

    model: str
    api_key: str | None = None
    """API key for the Gemini API or Vertex AI."""

    project: str | None = None
    """Google Cloud project ID (Vertex AI only)."""

    location: str | None = None
    """Vertex AI region, e.g. ``"us-central1"`` or ``"europe-west4"``."""

    credentials: "service_account.Credentials | None" = None
    """Service account credentials for Vertex AI. When set, ``api_key`` is not required."""

    vertexai: bool | None = None
    """Force backend selection: ``True`` for Vertex AI, ``False`` for Gemini API, ``None`` to auto-detect."""

    temperature: float | None = None
    """Sampling temperature in the range ``[0.0, 2.0]``."""


__all__ = [
    "AnthropicModel",
    "GoogleModel",
    "OpenAIModel",
    "PredefinedModel",
]
