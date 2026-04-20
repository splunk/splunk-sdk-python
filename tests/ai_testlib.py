from typing import override

from splunklib.ai.model import PredefinedModel
from tests.ai_test_model import (
    AnthropicBedrockModel,
    InternalAIModel,
    TestLLMSettings,
    create_model,
)
from tests.testlib import SDKTestCase


class AITestCase(SDKTestCase):
    _model: PredefinedModel | None = None
    _sonnet_model: PredefinedModel | None = None

    @override
    def setUp(self) -> None:
        super().setUp()

        # Our tests don't expect this app to be installed, if needed it is
        # installed on demand.
        for app in self.service.apps.list():  # pyright: ignore[reportUnknownVariableType]
            if app.name.lower() == "splunk_mcp_server":
                app.delete()
                self.restart_splunk()

    @property
    def test_llm_settings(self) -> TestLLMSettings:
        bedrock_model_id: str = self.opts.kwargs.get(
            "bedrock_model_id", ""
        )  # ignore: [reportUnknownVariableType]
        if bedrock_model_id:
            aws_region: str = self.opts.kwargs.get(
                "bedrock_aws_region", ""
            )  # ignore: [reportUnknownVariableType]
            base_model_id: str = self.opts.kwargs.get(
                "bedrock_base_model_id", ""
            )  # ignore: [reportUnknownVariableType]
            return TestLLMSettings(
                anthropic_bedrock=AnthropicBedrockModel(
                    model=bedrock_model_id,  # ignore: [reportUnknownVariableType]
                    aws_region=aws_region,  # ignore: [reportUnknownVariableType]
                    base_model_id=base_model_id,  # ignore: [reportUnknownVariableType]
                )
            )

        client_id: str = self.opts.kwargs["internal_ai_client_id"]
        client_secret: str = self.opts.kwargs["internal_ai_client_secret"]
        app_key: str = self.opts.kwargs["internal_ai_app_key"]
        token_url: str = self.opts.kwargs["internal_ai_token_url"]
        base_url: str = self.opts.kwargs["internal_ai_base_url"]
        return TestLLMSettings(
            internal_ai=InternalAIModel(
                client_id=client_id,
                client_secret=client_secret,
                app_key=app_key,
                token_url=token_url,
                base_url=base_url,
            )
        )

    async def model(self) -> PredefinedModel:
        if self._model is not None:
            return self._model

        model = await create_model(self.test_llm_settings)
        self._model = model
        return model

    async def sonnet_model(self) -> PredefinedModel:
        """Returns a Sonnet model for tests that require a more capable model.

        Falls back to the default model if no Sonnet config is provided.
        """
        if self._sonnet_model is not None:
            return self._sonnet_model

        sonnet_model_id: str = self.opts.kwargs.get("bedrock_sonnet_model_id", "")
        if sonnet_model_id:
            aws_region: str = self.opts.kwargs.get("bedrock_aws_region", "")
            base_model_id: str = self.opts.kwargs.get("bedrock_sonnet_base_model_id", "")
            settings = TestLLMSettings(
                anthropic_bedrock=AnthropicBedrockModel(
                    model=sonnet_model_id,
                    aws_region=aws_region,
                    base_model_id=base_model_id,
                )
            )
            model = await create_model(settings)
            self._sonnet_model = model
            return model

        return await self.model()

    @property
    def supports_provider_strategy(self) -> bool:
        """Returns True if the configured model supports ProviderStrategy (native JSON output).

        AnthropicBedrockModel routes through ToolStrategy instead, so it returns False.
        """
        return self.test_llm_settings.anthropic_bedrock is None
