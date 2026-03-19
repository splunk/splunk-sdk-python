from typing import override
from splunklib.ai.model import PredefinedModel
from tests.ai_test_model import InternalAIModel, TestLLMSettings, create_model
from tests.testlib import SDKTestCase


class AITestCase(SDKTestCase):
    _model: PredefinedModel | None = None

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
