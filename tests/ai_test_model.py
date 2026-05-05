import httpx
from pydantic import BaseModel

from splunklib.ai import OpenAIModel
from splunklib.ai.model import PredefinedModel


class InternalAIModel(BaseModel):
    client_id: str
    client_secret: str
    app_key: str

    token_url: str
    base_url: str


class TestLLMSettings(BaseModel):
    # TODO: Currently we only support our internal OpenAI-compatible model,
    # once we are close to GA we should also support OpenAI and probably Ollama, such
    # that external developers can also run our test suite suite locally.
    internal_ai: InternalAIModel | None = None


async def create_model(s: TestLLMSettings) -> PredefinedModel:
    if s.internal_ai is not None:
        return await _buildInternalAIModel(
            token_url=s.internal_ai.token_url,
            base_url=s.internal_ai.base_url,
            client_id=s.internal_ai.client_id,
            client_secret=s.internal_ai.client_secret,
            app_key=s.internal_ai.app_key,
        )
    raise Exception("unreachable")


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

    response.raise_for_status()

    token = _TokenResponse.model_validate_json(response.text).access_token

    model = "gpt-5-nano"

    return OpenAIModel(
        model=model,
        base_url=f"{base_url}/{model}",
        api_key="test-api-key",  # unused
        extra_body={"user": f'{{"appkey":"{app_key}"}}'},
        httpx_client=httpx.AsyncClient(headers={"api-key": token}),
        temperature=0.0,
    )
