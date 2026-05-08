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


from typing import Self

from pydantic import BaseModel, Field

from splunklib.binding import _spliturl
from splunklib.client import Service, connect


class SerializedService(BaseModel):
    management_url: str = ""
    username: str | None = None
    password: str | None = Field(default=None, repr=False)
    token: str | None = Field(default=None, repr=False)
    bearer_token: str | None = Field(default=None, repr=False)
    auth_cookies: dict[str, str] | None = Field(default=None, repr=False)

    @classmethod
    def from_service(cls, service: Service) -> Self:
        return cls(
            management_url=f"{service.scheme}://{service.host}:{service.port}",  # pyright: ignore[reportUnknownMemberType]
            username=service.username if service.username else None,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            password=service.password if service.password else None,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            token=service.token if isinstance(service.token, str) else None,  # pyright: ignore[reportUnknownMemberType, reportArgumentType]
            bearer_token=service.bearerToken if service.bearerToken else None,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            auth_cookies=(
                service.get_cookies() if len(service.get_cookies()) != 0 else None  # pyright: ignore[reportUnknownArgumentType]
            ),
        )

    def connect(self) -> Service:
        scheme, host, port, path = _spliturl(self.management_url)  # pyright: ignore[reportUnknownVariableType]
        return connect(
            scheme=scheme,  # pyright: ignore[reportUnknownArgumentType]
            host=host,  # pyright: ignore[reportUnknownArgumentType]
            port=port,
            path=path,
            username=self.username if self.username else None,
            password=self.password if self.password else None,
            token=self.token if self.token else None,
            splunkToken=self.bearer_token if self.bearer_token else None,
            cookie="; ".join(f"{key}={self.auth_cookies[key]}" for key in self.auth_cookies)
            if self.auth_cookies
            else None,
            autologin=True,
        )
