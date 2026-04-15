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

from tests import testlib


class TestJSONCustomRestEndpointsSpecialMethodHelpers(testlib.SDKTestCase):
    app_name = "cre_app"

    def test_GET(self):
        resp = self.service.get(
            app=self.app_name,
            path_segment="execute",
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "headers": {"x-bar": "baz"},
                "method": "GET",
            },
        )

    def test_POST(self):
        body = json.dumps({"foo": "bar"})
        resp = self.service.post(
            app=self.app_name,
            path_segment="execute",
            body=body,
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "payload": '{"foo": "bar"}',
                "headers": {"x-bar": "baz"},
                "method": "POST",
            },
        )

    def test_PUT(self):
        body = json.dumps({"foo": "bar"})
        resp = self.service.put(
            app=self.app_name,
            path_segment="execute",
            body=body,
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "payload": '{"foo": "bar"}',
                "headers": {"x-bar": "baz"},
                "method": "PUT",
            },
        )

    def test_PATCH(self):
        if self.service.splunk_version[0] < 10:
            self.skipTest("PATCH custom REST endpoints not supported on splunk < 10")

        body = json.dumps({"foo": "bar"})
        resp = self.service.patch(
            app=self.app_name,
            path_segment="execute",
            body=body,
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "payload": '{"foo": "bar"}',
                "headers": {"x-bar": "baz"},
                "method": "PATCH",
            },
        )

    def test_DELETE(self):
        # delete does allow specifying body and custom headers.
        resp = self.service.delete(
            app=self.app_name,
            path_segment="execute",
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "payload": "",
                "headers": {},
                "method": "DELETE",
            },
        )


class TestJSONCustomRestEndpointGenericRequest(testlib.SDKTestCase):
    app_name = "cre_app"

    def test_no_str_body_GET(self):
        def with_body():
            self.service.request(
                app=self.app_name, method="GET", path_segment="execute", body="str"
            )

        self.assertRaisesRegex(
            Exception, "Unable to set body on GET request", with_body
        )

    def test_GET(self):
        resp = self.service.request(
            app=self.app_name,
            method="GET",
            path_segment="execute",
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "headers": {"x-bar": "baz"},
                "method": "GET",
            },
        )

    def test_POST(self):
        self.method("POST")

    def test_PUT(self):
        self.method("PUT")

    def test_PATCH(self):
        if self.service.splunk_version[0] < 10:
            self.skipTest("PATCH custom REST endpoints not supported on splunk < 10")
        self.method("PATCH")

    def test_DELETE(self):
        self.method("DELETE")

    def method(self, method: str):
        body = json.dumps({"foo": "bar"})
        resp = self.service.request(
            app=self.app_name,
            method=method,
            path_segment="execute",
            body=body,
            headers=[("x-bar", "baz")],
        )
        self.assertIn(("x-foo", "bar"), resp.headers)
        self.assertEqual(resp.status, 200)
        self.assertEqual(
            json.loads(str(resp.body)),
            {
                "payload": '{"foo": "bar"}',
                "headers": {"x-bar": "baz"},
                "method": method,
            },
        )
