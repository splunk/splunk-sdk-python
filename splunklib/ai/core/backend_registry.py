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

from splunklib.ai.core.backend import Backend


def get_backend() -> Backend:
    """Get a backend instance."""
    # Lazy import to avoid circular dependency hell between LangChain and SDK
    from splunklib.ai.engines.langchain import langchain_backend_factory

    # NOTE: For now we're just using the langchain backend implementation
    return langchain_backend_factory()
