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

# This script uses unsupported API to download the Splunk MCP Server App
# from splunkbase for CI purposes.
#
# Use at your own risk.


import os
import xml.etree.ElementTree as ET

import httpx
from pydantic import BaseModel

SPLUNK_MCP_APP_ID = 7931
MCP_PATH = "splunk-mcp-server.tgz"
SPLUNKBASE_URL = "https://splunkbase.splunk.com"


class Release(BaseModel):
    path: str


class Response(BaseModel):
    release: Release


def run() -> None:
    username = os.environ["SPLUNKBASE_USERNAME"]
    password = os.environ["SPLUNKBASE_PASSWORD"]

    client = httpx.Client(follow_redirects=True)
    response = client.post(
        f"{SPLUNKBASE_URL}/api/account:login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )
    response.raise_for_status()

    response_xml = ET.fromstring(response.text)
    token = next(elem.text for elem in response_xml if elem.tag.endswith("id"))
    if token is None:
        raise AssertionError("token not found in the response")

    response = client.get(
        f"{SPLUNKBASE_URL}/api/v1/app/{SPLUNK_MCP_APP_ID}/?include=release",
        # ? Might not be needed here after all?
        # headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()

    result = Response.model_validate_json(response.text)

    response = client.get(
        result.release.path,
        headers={"X-Auth-Token": token},
    )
    response.raise_for_status()

    with open(MCP_PATH, "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    run()
