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
import csv
import gzip
import json
import os
import sys
from collections.abc import Sequence
from typing import Literal
from urllib.parse import urlsplit

# ! WARN: This insert is only needed for splunk-sdk-python CI/CD to work.
# ! Remove this if you're modifying this example locally.
sys.path.insert(0, "/splunklib-deps")

# Include all 3rd party dependencies from <app_name>/bin/lib/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from pydantic import BaseModel
from setup_logging import setup_logging  # pyright: ignore[reportImplicitRelativeImport]

from splunklib import client
from splunklib.ai import OpenAIModel
from splunklib.ai.agent import Agent
from splunklib.ai.messages import HumanMessage

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
SYSTEM_PROMPT = """You are a threat intelligence analyst. Your role is to assess the
severity of security alerts based on the provided alert data.

You will receive alert data containing a search name and a list of
result rows. Each row represents aggregated network activity that
triggered the alert.

Analyze the data and return a JSON object with the following fields:

- severity: "high" or "low"
- confidence: a float between 0 and 1 indicating how confident you are in the assessment
- summary: a brief explanation of your assessment in 2-3 sentences
- recommended_action: a short actionable recommendation

Respond only with valid JSON. Do not include any other text."""


APP_NAME = "ai_custom_alert_app"
logger = setup_logging(APP_NAME)


class AlertData(BaseModel):
    search_name: str
    search_results: Sequence[dict[str, str]]


class AgenticSeverityAssessment(BaseModel):
    severity: Literal["high", "low"]
    confidence: float  # Between 0 and 1
    summary: str
    recommended_action: str


async def invoke_agent(
    service: client.Service, alert_data: AlertData
) -> AgenticSeverityAssessment:
    user_prompt = f"Assess the severity of the alert triggered from {alert_data.search_name=}. {alert_data.search_results=}"

    async with Agent(
        model=LLM_MODEL,
        system_prompt=SYSTEM_PROMPT,
        service=service,
        output_schema=AgenticSeverityAssessment,
    ) as agent:
        logger.info(f"Invoking {agent.model=}")
        logger.debug(f"{user_prompt=}")
        result = await agent.invoke([HumanMessage(content=user_prompt)])
        return result.structured_output


def read_results_from_file(results_file_path: str) -> list[dict[str, str]]:
    alert_results: list[dict[str, str]] = []

    with gzip.open(results_file_path, "rt") as results_file:
        reader = csv.DictReader(results_file)
        alert_results = list(reader)

    logger.debug(f"{alert_results=}")
    return alert_results


def handle_alert() -> None:
    alert_payload_json: str = sys.stdin.read()
    alert_payload = json.loads(alert_payload_json)

    # When triggering a custom alert, a saved search passes its results to the alert
    # in a temporary file. We then read the file and pass its contents to the LLM.
    results_file_path = alert_payload.get("results_file", "")
    if not results_file_path:
        logger.error("No results file provided.")
        sys.exit(1)

    try:
        search_results = read_results_from_file(results_file_path)

        search_name = alert_payload.get("search_name", "")
        alert_data = AlertData(search_name=search_name, search_results=search_results)

        server_uri = alert_payload.get("server_uri")
        splunk_uri = urlsplit(server_uri, scheme="https")
        session_key = alert_payload.get("session_key")
        service = client.connect(
            scheme=splunk_uri.scheme,
            token=session_key,
            host=splunk_uri.hostname,
            port=splunk_uri.port,
            autologin=True,
        )
        severity_assessment = asyncio.run(invoke_agent(service, alert_data))
        logger.debug(f"{severity_assessment.model_dump_json()=}")

        configuration = alert_payload.get("configuration", {})
        logger.debug(f"{configuration=}")

        output_index = configuration.get("output_index", "main")
        output_sourcetype = configuration.get("output_sourcetype", "assessment")
        splunk_index: client.Index = service.indexes[output_index]  # pyright: ignore[reportUnknownVariableType]
        splunk_index.submit(
            severity_assessment.model_dump_json(),
            sourcetype=f"{APP_NAME}:{output_sourcetype}",
        )
    except Exception as e:
        logger.exception(f"Failed to write to Splunk: {e=}", stack_info=True)


if __name__ == "__main__":
    handle_alert()
