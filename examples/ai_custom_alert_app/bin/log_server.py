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


import json
import os
import random
import sys

# ! NOTE: This insert is only needed for splunk-sdk-python CI/CD to work.
# ! Remove this if you're modifying this example locally.
sys.path.insert(0, "/splunklib-deps")

# Include all 3rd party dependencies from <app_name>/bin/lib/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))


from splunklib import client

INTERNAL_IPS = ["10.0.0.5", "10.0.0.12", "10.0.0.34", "10.0.0.87"]
EXTERNAL_IPS = [
    "185.220.101.34",
    "91.219.236.222",
    "45.155.205.99",
    "198.51.100.78",
    "203.0.113.42",
]
DEST_PORTS = [80, 443, 8080, 22, 53, 3389]
ACTIONS = ["allowed", "blocked"]


def generate_event() -> dict[str, str | int]:
    return {
        "action": random.choice(ACTIONS),
        "src_ip": random.choice(INTERNAL_IPS),
        "dest_ip": random.choice(EXTERNAL_IPS),
        "dest_port": random.choice(DEST_PORTS),
    }


APP_NAME = "ai_custom_alert_app"
BURST_QUANTITY = 100


def log_server() -> None:
    print(f"Sending {BURST_QUANTITY} fake threat logs to Splunk!")
    try:
        splunk_service = client.connect(
            scheme="https",
            host="localhost",
            port=8089,
            username="admin",
            password="changed!",
            autologin=True,
        )

        splunk_index: client.Index = splunk_service.indexes["main"]
        for _ in range(BURST_QUANTITY):
            event = generate_event()
            splunk_index.submit(json.dumps(event), sourcetype=f"{APP_NAME}:threat_log")
            print(event)

        print("Fake threat logs sent!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    log_server()
