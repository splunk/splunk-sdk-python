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

from splunklib.ai.serialized_service import SerializedService
from tests import testlib


class TestSerializedService(testlib.SDKTestCase):
    def do_test_service(self, serialized: SerializedService) -> None:
        s = serialized.connect()
        s.info  # make sure connection works
        SerializedService.from_service(s).connect().info  # Wrap and unwrap again

    def test_testlib_service(self) -> None:
        service = SerializedService.from_service(self.service)
        assert service.management_url
        assert service.username
        assert service.password
        assert service.auth_cookies is not None
        assert service.token  # populated after self.service.login
        assert len(service.auth_cookies) == 1
        assert service.auth_cookies.get(
            "splunkd_8089"
        )  # populated after self.service.login
        assert service.bearer_token is None

        self.do_test_service(service)

    def test_username_and_password(self) -> None:
        service = SerializedService.from_service(self.service)
        self.do_test_service(
            SerializedService(
                management_url=service.management_url,
                username=service.username,
                password=service.password,
            )
        )

    def test_token(self) -> None:
        service = SerializedService.from_service(self.service)
        self.do_test_service(
            SerializedService(
                management_url=service.management_url,
                token=service.token,
            )
        )

    def test_cookie(self) -> None:
        service = SerializedService.from_service(self.service)
        self.do_test_service(
            SerializedService(
                management_url=service.management_url,
                auth_cookies=service.auth_cookies,
            )
        )

    def get_splunk_bearer_token(self) -> str:
        res = self.service.post(
            path_segment="authorization/tokens",
            name=self.service.username,
            audience="test",
            type="ephemeral",
            output_mode="json",
        )
        token = json.loads(str(res.body))["entry"][0]["content"]["token"]
        return token

    def test_bearer_token(self) -> None:
        service = SerializedService.from_service(self.service)
        self.do_test_service(
            SerializedService(
                management_url=service.management_url,
                bearer_token=self.get_splunk_bearer_token(),
            )
        )
