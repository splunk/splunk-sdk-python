import functools
import inspect
import json
import os
from collections.abc import Callable, Coroutine
from typing import Any, override
from unittest.mock import patch
from urllib import parse
from warnings import warn

import vcr
from vcr.config import RecordMode
from vcr.request import Request

from splunklib.ai.messages import AIMessage, ContentBlock, TextBlock
from splunklib.ai.model import PredefinedModel
from tests.ai_test_model import InternalAIModel, TestLLMSettings, create_model
from tests.testlib import SDKTestCase

REDACTED_APP_KEY = "[[[--APPKEY-REDACTED-]]]"


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

    def _parse_content_block(self, block: str | ContentBlock) -> str | None:
        match block:
            case TextBlock():
                return block.text
            case str():
                return block
            case _:
                warn("Skipping OpaqueBlock when parsing the AIMessage.content")
                return None

    def parse_content(self, message: AIMessage) -> str:
        """Parses the content from AIMessage and builds a single string our of it"""
        if isinstance(message.content, str):
            return message.content

        return " ".join(
            parsed_block
            for block in message.content
            if (parsed_block := self._parse_content_block(block))
        )

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


def ai_snapshot_test() -> Callable[
    [Callable[..., Coroutine[Any, Any, None]]], Callable[..., Coroutine[Any, Any, None]]
]:
    def decorator(
        fn: Callable[..., Coroutine[Any, Any, None]],
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        source_file = inspect.getfile(fn)
        test_dir = os.path.dirname(source_file)
        test_file = os.path.splitext(os.path.basename(source_file))[0]

        snapshot_dir = os.path.join(test_dir, "snapshots", test_file)
        snapshot_filename = f"{fn.__qualname__}.json"

        @functools.wraps(fn)
        async def wrapper(self: AITestCase, *args: Any, **kwargs: Any) -> None:
            settings = self.test_llm_settings
            assert settings.internal_ai is not None

            internal_ai_hostname = parse.urlparse(settings.internal_ai.base_url).hostname
            assert internal_ai_hostname is not None

            class _JSONFriendlySerializer:
                def deserialize(self, serialized: str) -> Any:
                    assert settings.internal_ai is not None
                    serialized = serialized.replace(REDACTED_APP_KEY, settings.internal_ai.app_key)

                    data = json.loads(serialized)
                    for interaction in data.get("interactions", []):
                        interaction["request"]["uri"] = interaction["request"]["uri"].replace(
                            "internal-ai-host", internal_ai_hostname, 1
                        )

                        interaction["request"]["body"] = json.dumps(interaction["request"]["body"])
                        body = interaction["response"]["body"]
                        interaction["response"]["body"] = {}
                        interaction["response"]["body"]["string"] = json.dumps(body)

                    return data

                def serialize(self, dict: Any) -> str:
                    for interaction in dict.get("interactions", []):
                        interaction["request"]["uri"] = interaction["request"]["uri"].replace(
                            internal_ai_hostname, "internal-ai-host", 1
                        )

                        body = interaction["request"]["body"]
                        interaction["request"]["body"] = json.loads(body)

                        resp_body = interaction["response"]["body"]["string"]
                        interaction["response"]["body"] = json.loads(resp_body)

                    out = json.dumps(dict, indent=4) + "\n"
                    assert settings.internal_ai is not None
                    out = out.replace(settings.internal_ai.app_key, REDACTED_APP_KEY)

                    # Assert that nothing is leaking into the public snapshots.
                    assert internal_ai_hostname not in out.lower()
                    assert settings.internal_ai.app_key.lower() not in out.lower()
                    assert settings.internal_ai.base_url.lower() not in out.lower()
                    assert settings.internal_ai.token_url.lower() not in out.lower()
                    assert settings.internal_ai.client_id.lower() not in out.lower()
                    assert settings.internal_ai.client_secret.lower() not in out.lower()

                    return out

            def _before_record_request(request: Request) -> Request | None:
                url = parse.urlparse(request.uri)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                if url.hostname == internal_ai_hostname:
                    request.headers = {}
                    return request
                return None

            def _before_record_response(response: Any) -> Any:
                response["headers"] = {}
                return response

            def _json_body_matcher(r1: Any, r2: Any) -> None:
                b1 = json.loads(r1.body)
                b2 = json.loads(r2.body)
                if b1 != b2:
                    raise AssertionError(f"Body mismatch:\n{b1}\n!=\n{b2}")

            my_vcr = vcr.VCR(
                cassette_library_dir=snapshot_dir,
                serializer="json-friendly",
                record_mode=RecordMode.ONCE,
                match_on=[
                    "method",
                    "scheme",
                    "host",
                    "port",
                    "path",
                    "query",
                    "jsonbody",
                ],
                before_record_request=_before_record_request,
                before_record_response=_before_record_response,
                record_on_exception=False,
                drop_unused_requests=True,
            )
            my_vcr.register_serializer("json-friendly", _JSONFriendlySerializer())
            my_vcr.register_matcher("jsonbody", _json_body_matcher)

            with my_vcr.use_cassette(snapshot_filename):
                await fn(self, *args, **kwargs)

        return wrapper

    return decorator


def deterministic_thread_ids() -> Callable[
    [Callable[..., Coroutine[Any, Any, None]]], Callable[..., Coroutine[Any, Any, None]]
]:
    def decorator(
        fn: Callable[..., Coroutine[Any, Any, None]],
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        @functools.wraps(fn)
        async def wrapper(self: AITestCase, *args: Any, **kwargs: Any) -> None:
            counter = 0

            def _deterministic_uuid() -> str:
                nonlocal counter
                result = f"00000000-0000-0000-0000-{counter:012d}"
                counter += 1
                return result

            with patch(
                "splunklib.ai.engines.langchain._thread_id_new_uuid",
                side_effect=_deterministic_uuid,
            ):
                await fn(self, *args, **kwargs)

        return wrapper

    return decorator
