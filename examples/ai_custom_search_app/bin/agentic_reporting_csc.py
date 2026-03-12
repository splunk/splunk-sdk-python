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
import asyncio
import json
import os
import sys
from collections.abc import Generator, Sequence
from typing import Any, final, override

from setup_logging import setup_logging  # pyright: ignore[reportImplicitRelativeImport]

# ! WARN: This insert is only needed for splunk-sdk-python CI/CD to work.
# ! Remove this if you're modifying this example locally.
sys.path.insert(0, "/splunklib-deps")

# Include all 3rd party dependencies from <app_name>/bin/lib/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from pydantic import BaseModel, Field

from splunklib.ai import OpenAIModel
from splunklib.ai.agent import Agent
from splunklib.ai.messages import HumanMessage
from splunklib.data import Record
from splunklib.searchcommands import (
    Configuration,
    Option,
    dispatch,  # pyright: ignore[reportPrivateLocalImportUsage]
    validators,
)
from splunklib.searchcommands.eventing_command import EventingCommand

# BUG: For some reason the process is started with its trust store path overridden with
# one that might not exist on the filesystem. In such case we unset the env, which
# causes the default Certificate Authorities to be used instead.
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(
    CA_TRUST_STORE
):
    del os.environ["SSL_CERT_FILE"]

APP_NAME = "ai_custom_search_app"
logger = setup_logging(APP_NAME)


LLM_MODEL = OpenAIModel(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1",
    # To store API keys, consider secret storage:
    # https://dev.splunk.com/enterprise/docs/developapps/manageknowledge/secretstorage/secretstoragepython
    api_key="<super_secret_key>",
)


class AgentOutput(BaseModel):
    """Output schema model for the LLM-based Agent."""

    should_keep: bool = Field(
        description="If False, filter a record out of the pipeline.", default=True
    )
    is_relevant: bool = Field(
        description="Should event be highlighted in a table view.", default=False
    )


@final
@Configuration()
class AgenticReportingCSC(EventingCommand):
    """agenticreport provides an assortment of example integrations with an LLM Agent.

    Example:
    ```
    | makeresults count=10 | streamstats count as _row
    | agenticreport should_filter="true" highlight_topic="Is this record's _row odd?"
    ```
    """

    should_filter = Option(
        doc="Should irrelevant records be filtered out",
        require=False,
        default=False,
        validate=validators.Boolean(),
    )
    highlight_topic = Option(
        doc="What to consider when deciding to highlight a record",
        require=False,
        default=False,
    )

    @override
    def transform(self, records: Sequence[Record]) -> Generator[Record, Any]:
        logger.info(
            "Begin transform() in `agenticreport` with "
            + f"options: {self.should_filter=}, {self.highlight_topic=}"
        )

        for record in records:
            if not record:
                continue

            record_json = json.dumps(record)
            logger.debug(f"{record_json=}")

            user_prompt = f"""
Analyze this log: "{record_json}" and perform these tasks:

1. Decide if record matches the intent: "{self.should_filter}"?
    (Return boolean `should_keep`)
2. Is this log relevant to "{self.highlight_topic}"?
    (Return boolean `is_relevant`)
"""
            try:
                llm_analysis = asyncio.run(self.invoke_agent(user_prompt))
                logger.debug(f"{llm_analysis.model_dump_json()=}")
                if self.should_filter and not llm_analysis.should_keep:
                    # Filter the record out of the results
                    continue

                if self.highlight_topic:
                    self.add_field(record, "should_keep", llm_analysis.is_relevant)
            except Exception as e:
                logger.exception(e)
                self.add_field(record, "agent_error", e)
            finally:
                yield record

        logger.debug("Finish transform() in `agenticreport`")

    async def invoke_agent(self, prompt: str) -> AgentOutput:
        assert self.service, "No Splunk connection available"

        async with Agent(
            model=OpenAIModel(
                model="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
                # To store API keys, consider secret storage:
                # https://dev.splunk.com/enterprise/docs/developapps/manageknowledge/secretstorage/secretstoragepython
                api_key="<super_secret_key>",
            ),
            system_prompt="You are an Expert Splunk Data Analyst.",
            service=self.service,
            output_schema=AgentOutput,
        ) as agent:
            logger.info(f"Invoking {LLM_MODEL.model} at {LLM_MODEL.base_url}")
            result = await agent.invoke([HumanMessage(content=prompt)])
            return result.structured_output


dispatch(AgenticReportingCSC, sys.argv, sys.stdin, sys.stdout, __name__)
