#
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
import base64
import traceback
from abc import abstractmethod
from http.cookies import SimpleCookie

from splunklib.ai.model import PredefinedModel
from splunklib.binding import _spliturl
from splunklib.client import Service, connect
from tests.ai_test_model import TestLLMSettings, create_model

try:
    import splunk

    class CRETestHandler(splunk.rest.BaseRestHandler):
        _service: Service | None = None
        _model: PredefinedModel | None = None

        def handle_POST(self) -> None:
            async def run() -> None:
                try:
                    await self.run()
                except Exception:
                    trace = traceback.format_exc()
                    self.response.setStatus(500)
                    self.response.write(trace)
                    return

                self.response.setStatus(200)

            asyncio.run(run())

        @abstractmethod
        async def run(self) -> None: ...

        async def model(self) -> PredefinedModel:
            if self._model is not None:
                return self._model

            raw_body = str(self.request["payload"])
            s = TestLLMSettings.model_validate_json(raw_body)
            model = await create_model(s)
            self._model = model
            return model

        @property
        def service(self) -> Service:
            if self._service is not None:
                return self._service

            mngmt_url: str = splunk.getLocalServerInfo()
            scheme, host, port, path = _spliturl(mngmt_url)

            headers = self.request["headers"]

            cookies: str | None = headers.get("cookie")
            authorizaiton: str | None = headers.get("authorization")

            if cookies is not None:
                c = SimpleCookie()
                c.load(cookies)
                cookie_token = c.get("splunkd_8089")
                if cookie_token is not None:
                    service = connect(
                        scheme=scheme,
                        host=host,
                        port=port,
                        path=path,
                        autologin=True,
                        cookie=f"splunkd_8089: {cookie_token}",
                    )

                    # Make sure splunk connection works.
                    assert service.info.startup_time

                    self._service = service
                    return service

            if authorizaiton is not None:
                authType, token = authorizaiton.split(" ", 1)
                if authType.lower() == "bearer" or authType.lower() == "splunk":
                    service = connect(
                        scheme=scheme,
                        host=host,
                        port=port,
                        path=path,
                        autologin=True,
                        token=token,
                    )

                    # Make sure splunk connection works.
                    assert service.info.startup_time

                    self._service = service
                    return service
                elif authType.lower() == "basic":
                    decoded_bytes = base64.b64decode(token)
                    username, password = decoded_bytes.decode("utf-8").split(":", 1)
                    service = connect(
                        scheme=scheme,
                        host=host,
                        port=port,
                        path=path,
                        autologin=True,
                        username=username,
                        password=password,
                    )

                    # Make sure splunk connection works.
                    assert service.info.startup_time

                    self._service = service
                    return service

            # We should not reach here, since Splunk requires that the request is authenticated.
            raise Exception("Missing auth")
except ImportError as e:
    # The "splunk" package is only available on the Splunk instances, as it is only shipped
    # with the default splunk python interpreter. We can't use it reliabely if used outside of
    # splunk, in such cases, we don't expose the wrapped class.
    if e.name != "splunk":
        raise
