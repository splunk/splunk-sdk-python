from collections.abc import Generator

import pytest
from langchain_core.language_models import BaseChatModel

from splunklib.ai.engines import langchain as lc_engine
from splunklib.ai.model import PredefinedModel
from tests.ai_test_model import AnthropicBedrockModel

_original_create_langchain_model = lc_engine._create_langchain_model  # pyright: ignore[reportPrivateUsage]


def _patched_create_langchain_model(model: PredefinedModel) -> BaseChatModel:
    if isinstance(model, AnthropicBedrockModel):
        return model._to_langchain_model()  # pyright: ignore[reportPrivateUsage]
    return _original_create_langchain_model(model)


@pytest.fixture(autouse=True)
def _patch_langchain_model_factory(request: pytest.FixtureRequest) -> Generator[None]:
    if "integration/ai" not in str(request.fspath):
        yield
        return
    lc_engine._create_langchain_model = _patched_create_langchain_model  # pyright: ignore[reportPrivateUsage]
    yield
    lc_engine._create_langchain_model = _original_create_langchain_model  # pyright: ignore[reportPrivateUsage]
