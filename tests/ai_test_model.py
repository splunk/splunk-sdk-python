import collections.abc
from dataclasses import dataclass
from typing import Any, override

import httpx
from httpx import Auth, Request, Response
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from splunklib.ai import AnthropicModel, OpenAIModel
from splunklib.ai.model import PredefinedModel


class InternalAIModel(BaseModel):
    client_id: str
    client_secret: str
    app_key: str

    token_url: str
    base_url: str


@dataclass(frozen=True)
class AnthropicBedrockModel(AnthropicModel):
    """Anthropic model accessed via AWS Bedrock, for testing only."""

    api_key: str = ""
    base_url: str = ""
    aws_region: str = ""
    base_model_id: str = ""

    def _to_langchain_model(self) -> BaseChatModel:
        try:
            from langchain_aws import ChatBedrockConverse

            kwargs: dict[str, Any] = {"model": self.model}
            if self.aws_region:
                kwargs["region_name"] = self.aws_region
            if self.temperature is not None:
                kwargs["temperature"] = self.temperature
            if self.model.startswith("arn:"):
                kwargs["provider"] = "anthropic"
                kwargs["base_model_id"] = (
                    self.base_model_id or "anthropic.claude-haiku-4-5-20251001"
                )
            return ChatBedrockConverse(**kwargs)
        except ImportError:
            raise ImportError(
                "AWS Bedrock support is not installed.\n"
                + "To enable Bedrock models, install the optional extra:\n"
                + 'pip install "splunk-sdk[bedrock]"\n'
                + "# or if using uv:\n"
                + "uv add splunk-sdk[bedrock]"
            )


class TestLLMSettings(BaseModel):
    # TODO: Currently we only support our internal OpenAI-compatible model,
    # once we are close to GA we should also support OpenAI and probably Ollama, such
    # that external developers can also run our test suite suite locally.
    internal_ai: InternalAIModel | None = None
    anthropic_bedrock: AnthropicBedrockModel | None = None


async def create_model(s: TestLLMSettings) -> PredefinedModel:
    if s.anthropic_bedrock is not None:
        return s.anthropic_bedrock
    if s.internal_ai is not None:
        return await _buildInternalAIModel(
            token_url=s.internal_ai.token_url,
            base_url=s.internal_ai.base_url,
            client_id=s.internal_ai.client_id,
            client_secret=s.internal_ai.client_secret,
            app_key=s.internal_ai.app_key,
        )
    raise Exception("unreachable")


class _InternalAIAuth(Auth):
    token: str

    def __init__(self, token: str) -> None:
        self.token = token

    @override
    def auth_flow(
        self, request: Request
    ) -> collections.abc.Generator[Request, Response]:
        request.headers["api-key"] = self.token
        yield request


class _TokenResponse(BaseModel):
    access_token: str


async def _buildInternalAIModel(
    token_url: str,
    base_url: str,
    client_id: str,
    client_secret: str,
    app_key: str,
) -> OpenAIModel:
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    http = httpx.AsyncClient()
    response = await http.post(
        url=token_url,
        headers=headers,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )

    token = _TokenResponse.model_validate_json(response.text).access_token

    auth_handler = _InternalAIAuth(token)
    model = "gpt-5-nano"

    return OpenAIModel(
        model=model,
        base_url=f"{base_url}/{model}",
        api_key="",  # unused
        extra_body={"user": f'{{"appkey":"{app_key}"}}'},
        httpx_client=httpx.AsyncClient(auth=auth_handler),
        temperature=0.0,
    )
