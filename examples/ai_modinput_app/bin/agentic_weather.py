# Copyright 2011-2026 Splunk, Inc.
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
import csv
import json
import os
import sys
from _collections_abc import dict_items
from typing import final, override

# ! NOTE: This insert is only needed for splunk-sdk-python CI/CD to work.
# ! Remove this if you're modifying this example locally.
sys.path.insert(0, "/splunklib-deps")

# Include all 3rd party dependencies from <app_name>/bin/lib/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from setup_logging import setup_logging  # pyright: ignore[reportImplicitRelativeImport]

from splunklib.ai import OpenAIModel
from splunklib.ai.agent import Agent
from splunklib.ai.messages import HumanMessage
from splunklib.modularinput.argument import Argument
from splunklib.modularinput.event import Event
from splunklib.modularinput.event_writer import EventWriter
from splunklib.modularinput.input_definition import InputDefinition
from splunklib.modularinput.scheme import Scheme
from splunklib.modularinput.script import Script

# BUG: For some reason the process is started with its trust store path overridden with
# one that might not exist on the filesystem. In such case we unset the env, which
# causes the default Certificate Authorities to be used instead.
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(
    CA_TRUST_STORE
):
    del os.environ["SSL_CERT_FILE"]


LLM_MODEL = OpenAIModel(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1",
    # To store API keys, consider secret storage:
    # https://dev.splunk.com/enterprise/docs/developapps/manageknowledge/secretstorage/secretstoragepython
    api_key="<super_secret_key>",
)

APP_NAME = "ai_modinput_app"
logger = setup_logging(APP_NAME)


@final
class AgenticWeatherModInput(Script):
    @override
    def get_scheme(self) -> Scheme:  # pyright: ignore[reportIncompatibleMethodOverride]
        scheme = Scheme("Agentic Weather")

        csv_file_path = Argument(
            name="csv_file_path",
            title="CSV file path",
            data_type=Argument.data_type_string,
            description="Path to file to read the weather logs from",
            required_on_create=True,
            required_on_edit=True,
        )
        scheme.add_argument(csv_file_path)
        return scheme

    @override
    def stream_events(self, inputs: InputDefinition, ew: EventWriter) -> None:
        input_items: dict_items[str, dict[str, str]] = inputs.inputs.items()  # pyright: ignore[reportUnknownVariableType]
        for input_name, input_params in input_items:
            logger.info(f"Beginning agentic enrichment for {input_name}.")
            logger.debug(f"{input_params=}")

            csv_file_path = input_params.get("csv_file_path", "")
            output_index = input_params.get("index", "")
            output_sourcetype = input_params.get("sourcetype", "")
            try:
                weather_events: list[dict[str, str | int]] = []
                with open(csv_file_path) as csv_file:
                    logger.info(f"Parsing search results from {csv_file_path}")
                    reader = csv.DictReader(csv_file)
                    weather_events += list(reader)

                for weather_event in weather_events:
                    weather_event["human_readable"] = asyncio.run(
                        self.invoke_agent(json.dumps(weather_event))
                    )
                    logger.debug(f"{weather_event=}")

                    event = Event(
                        stanza=csv_file_path,
                        index=output_index,
                        sourcetype=output_sourcetype,
                        data=json.dumps(weather_event),
                    )
                    ew.write_event(event)
            except Exception as e:
                logger.exception(e, stack_info=True)

            logger.debug(f"Finishing enrichment for {input_name} at {csv_file_path}")

    async def invoke_agent(self, data_json: str) -> str:
        if not self.service:
            raise AssertionError("No Splunk connection available")

        logger.info(f"Invoking {LLM_MODEL.model} at {LLM_MODEL.base_url}")
        async with Agent(
            model=LLM_MODEL,
            system_prompt="You're an expert meteorologist.",
            service=self.service,
        ) as agent:
            prompt = (
                f"Parse {data_json=} into a into a short, human-readable sentence. "
                + "Was it a good day to go outside if you're human?"
            )
            response = await agent.invoke([HumanMessage(role="user", content=prompt)])
            logger.debug(f"{response=}")
            return response.messages[-1].content


if __name__ == "__main__":
    sys.exit(AgenticWeatherModInput().run(sys.argv))
