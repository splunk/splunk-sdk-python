#
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

from dataclasses import dataclass


@dataclass(frozen=True)
class PredefinedModel:
    """Base class for models that are predefined in the SDK"""

    model: str


@dataclass(frozen=True)
class OpenAIModel(PredefinedModel):
    """Predifned OpenAI Model"""

    # TODO: For the MVP purposes the configuration is pretty simple.
    # It will be extended in the future with additional fields.
    model: str
    base_url: str
    api_key: str
    temperature: float | None = None


__all__ = [
    "PredefinedModel",
    "OpenAIModel",
]
