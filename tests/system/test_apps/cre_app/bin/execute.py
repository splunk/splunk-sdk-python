import json
import os
import sys

sys.path.insert(0, "/splunklib-deps")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))


import splunk.rest


class Handler(splunk.rest.BaseRestHandler):
    def handle_GET(self):
        self.response.setHeader("Content-Type", "application/json")
        self.response.setHeader("x-foo", "bar")
        self.response.status = 200
        self.response.write(
            json.dumps(
                {
                    "headers": self.headers(),
                    "method": "GET",
                }
            )
        )

    def handle_DELETE(self):
        self.handle_with_payload("DELETE")

    def handle_POST(self):
        self.handle_with_payload("POST")

    def handle_PUT(self):
        self.handle_with_payload("PUT")

    def handle_PATCH(self):
        self.handle_with_payload("PATCH")

    def handle_with_payload(self, method):
        self.response.setHeader("Content-Type", "application/json")
        self.response.setHeader("x-foo", "bar")
        self.response.status = 200
        self.response.write(
            json.dumps(
                {
                    "payload": self.request.get("payload"),
                    "headers": self.headers(),
                    "method": method,
                }
            )
        )

    def headers(self):
        return {
            k: v for k, v in self.request.get("headers", {}).items() if k.lower().startswith("x")
        }
