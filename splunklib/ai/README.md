# Agentic Splunk SDK

## Overview

The Agentic Splunk SDK (`splunklib.ai`) allows Splunk app developers to embed LLM-powered
agents directly into their applications. It provides a provider-agnostic Agent abstraction
for model interaction, tool usage, and structured I/O.

## Basic Agent usage

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.messages import HumanMessage
from splunklib.client import connect

service = connect(
    scheme="https",
    host="localhost",
    port=8089,
    username="user",
    password="password",
    autologin=True,
)

model = OpenAIModel(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1",
    api_key="SECRET",
)

async with Agent(
    model=model,
    system_prompt="Your name is Stefan",
    service=service,
) as agent:
    result = await agent.invoke([HumanMessage(content="What is your name?")])

    print(result.final_message.content)  # My name is Stefan
```

## Models

The Agent is designed with a modular, provider-agnostic architecture. This allows a single Agent implementation
to work with different model providers through a common interface, without requiring changes to the agent’s core logic.

We support following predefined models:

- `OpenAIModel` - works with OpenAI and any [OpenAI-compatible API](https://platform.openai.com/docs/api-reference).
- `AnthropicModel` - works with Anthropic and any [Anthropic-compatible API](https://docs.anthropic.com/en/api).
- `GoogleModel` - works with Google's Gemini models via the [Gemini API](https://ai.google.dev/gemini-api/docs) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview).

### OpenAI

```py
from splunklib.ai import Agent, OpenAIModel

model = OpenAIModel(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1",
    api_key="SECRET",
)

async with Agent(model=model) as agent: ....
```

### Anthropic

```py
from splunklib.ai import Agent, AnthropicModel

model = AnthropicModel(
    model="claude-haiku-4-5-20251001",
    base_url="https://api.anthropic.com",
    api_key="SECRET",
)

async with Agent(model=model) as agent: ....
```

### Google

`GoogleModel` supports two backends: the [Gemini API](https://ai.google.dev/gemini-api/docs) and [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview).
The backend is selected automatically based on the parameters you provide, or you can
force it with the `vertexai` flag.

Requires the `google` optional extra:

```sh
pip install "splunk-sdk[google]"
# or with uv:
uv add splunk-sdk[google]
```

#### Gemini API

Use this when you have a Google AI Studio API key and do not need Vertex AI infrastructure.
Only `model` and `api_key` are required.

```py
from splunklib.ai import Agent, GoogleModel

model = GoogleModel(
    model="gemini-2.0-flash",
    api_key="YOUR_GOOGLE_API_KEY",
)

async with Agent(model=model) as agent:
    ...
```

#### Vertex AI - API key

Use this to route requests through Vertex AI with an API key. Providing `project` is enough
for the SDK to switch to the Vertex AI backend automatically.

```py
from splunklib.ai import Agent, GoogleModel

model = GoogleModel(
    model="gemini-2.0-flash",
    api_key="YOUR_VERTEX_API_KEY",
    project="your-gcp-project-id",
    # location="us-central1",  # optional, defaults to us-central1
)

async with Agent(model=model) as agent:
    ...
```

#### Vertex AI - service account credentials

Use this when authenticating with a service account key file (or any
`google.auth.credentials.Credentials`-compatible object). No `api_key` is needed.

```py
from google.oauth2 import service_account
from splunklib.ai import Agent, GoogleModel

credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

model = GoogleModel(
    model="gemini-2.0-flash",
    project="your-gcp-project-id",
    credentials=credentials,
    # location="us-central1",  # optional, defaults to us-central1
)

async with Agent(model=model) as agent:
    ...
```

#### Backend selection rules

| `project` | `credentials` | `vertexai` | Backend used |
|---|---|---|---|
| not set | not set | `None` (default) | Gemini API |
| set | - | `None` (default) | Vertex AI |
| - | set | `None` (default) | Vertex AI |
| any | any | `True` | Vertex AI (forced) |
| any | any | `False` | Gemini API (forced) |

### Self-hosted models via Ollama

[Ollama](https://ollama.com/) can serve local models with both OpenAI and Anthropic-compatible endpoints, so either model class works.

#### Using `OpenAIModel` with Ollama

See [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) for supported features.

```py
from splunklib.ai import Agent, OpenAIModel

model = OpenAIModel(
    model="llama3.2:3b",
    base_url="http://localhost:11434/v1",
    api_key="",  # required but ignored
)

async with Agent(model=model) as agent: ....
```

#### Using `AnthropicModel` with Ollama

See [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility) for supported features.

```py
from splunklib.ai import Agent, AnthropicModel

model = AnthropicModel(
    model="llama3.2:3b",
    base_url="http://localhost:11434",
    api_key="",  # required but ignored
)

async with Agent(model=model) as agent: ....
```

## Messages

`Agent.invoke` processes a list of `BaseMessage` objects and returns an `AgentResponse` containing the updated message history and optional structured output.

`BaseMessage` is a base class, that is extended by:

- `HumanMessage` — A message originating from the human/user.
- `AIMessage` — A message generated by the LLM.
- `SystemMessage` — A message used to prime or control agent behavior.
- `ToolMessage` — A message containing the result of a tool invocation.
- `SubagentMessage` — A message containing the result of a subagent invocation

## MCP tools

To enable the Agent to perform background or auxiliary tasks, it can be extended with MCP tools.
These tools provide the Agent with additional capabilities beyond text generation, such as executing
actions, fetching data, or interacting with external systems.

The `tool_settings` parameter controls which MCP tools are exposed to the underlying LLM. See [Tool filtering](#tool-filtering).

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.tool_settings import ToolSettings
from splunklib.client import connect

model = OpenAIModel(...)
service = connect(...)

async with Agent(
    model=model,
    system_prompt="Your name is Stefan",
    service=service,
    tool_settings=ToolSettings(local=True, remote=None),
) as agent:
    ...
```

### Remote tools

Remote tools are provided by the [Splunk MCP Server App](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/about-the-mcp-server-for-splunk-platform).
When a Splunk instance has the MCP Server App installed and configured, the Agent automatically
discovers and loads all tools that are enabled on the MCP server during construction.

To let an agent access remote tools, pass a `RemoteToolSettings` instance and all the appropriate tools whitelisted:

```py
from splunklib.ai.tool_settings import RemoteToolSettings, ToolAllowlist, ToolSettings

async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    tool_settings=ToolSettings(
        remote=RemoteToolSettings(
            allowlist=ToolAllowlist(names=["splunk_get_indexes"], tags=["tag1"])
        )
    ),
) as agent:
    ...
```

See [Tool filtering](#tool-filtering) for more details.

### Local tools

Local tools are custom tools that you, as an app developer, can implement and expose to the Agent.
These tools must be defined within your app in a file named: `bin/tools.py`

Local tools are registered using the ToolRegistry provided by the SDK. The registry exposes a `tool`
decorator, which is used to annotate Python functions that should be made available as tools to the Agent.

Each annotated function becomes an invocable tool, with its signature and docstring used to define
the tool’s interface and description.

Example `tools.py` implementation:

```py
from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool()
def hello(name: str) -> str:
    """Returns a hello message"""
    return f"Hello {name}!"


if __name__ == "__main__":
    registry.run()
```

To let an agent access all local tools, set `local=True`. To enable only some tools, pass a `LocalToolSettings` instance:

```py
from splunklib.ai.tool_settings import LocalToolSettings, ToolAllowlist, ToolSettings

async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    tool_settings=ToolSettings(
        # local=True,  # enable all local tools
        local=LocalToolSettings(allowlist=ToolAllowlist(names=["tool1"], tags=["tag1"])),
        remote=None,
    ),
) as agent:
    ...
```

See [Tool filtering](#tool-filtering) for more details.

#### ToolContext

`ToolContext` is a special parameter type that tools may declare in their function signature.
Unlike regular tool inputs, this parameter is not provided by the LLM. Instead, it is
automatically injected by the runtime for every tool invocation.

##### Service access

`ToolContext` provides access to the SDK’s `Service` object, allowing tools to perform
authenticated actions against Splunk on behalf of the **user who executed the Agent**.

```py
from splunklib.ai.registry import ToolContext, ToolRegistry
from splunklib.results import JSONResultsReader

registry = ToolRegistry()


@registry.tool()
def run_splunk_query(ctx: ToolContext) -> list[str]:
    stream = ctx.service.jobs.oneshot(
        "| makeresults count=10 | streamstats count as row_num",
        output_mode="json",
    )

    result = JSONResultsReader(stream)
    output: list[str] = []
    for r in result:
        if isinstance(r, dict):
            output.append(r["row_num"])

    return output


if __name__ == "__main__":
    registry.run()
```

##### Logger access

`ToolContext` exposes a `Logger` instance that can be used for logging within your tool implementation.

```py
from splunklib.ai.registry import ToolContext


@registry.tool()
def tool(ctx: ToolContext) -> None:
    ctx.logger.info("executing tool")
```

In this example, the `Logger` instance is accessed via `ctx.logger` and used to emit an informational
log message during tool execution.

These logs are forwarded to the `logger` passed to the `Agent` constructor.

### Tool filtering

Remote tools must be intentionally allowlisted before they are made available to the LLM.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.tool_settings import (
    LocalToolSettings,
    RemoteToolSettings,
    ToolAllowlist,
    ToolSettings,
)
from splunklib.client import connect

model = OpenAIModel(...)
service = connect(...)

async with Agent(
    model=model,
    system_prompt="Your name is Stefan",
    service=service,
    tool_settings=ToolSettings(
        local=True,
        remote=RemoteToolSettings(
            allowlist=ToolAllowlist(names=["tool_name"], tags=["tag1", "tag2"])
        ),
    ),
) as agent:
    ...
```

A `custom_predicate` can be used for more flexible filtering:

```py
tool_settings = ToolSettings(
    local=LocalToolSettings(
        allowlist=ToolAllowlist(custom_predicate=lambda tool: tool.name.startswith("my_"))
    ),
    remote=None,
)
```

As a shorthand, pass `local=True` to load all local tools with no filtering:

```py
tool_settings = ToolSettings(local=True, remote=None)
```

## Conversation stores

By default, each call to `agent.invoke` is stateless - the agent has no memory of previous interactions,
unless you provide the previous message history explicitly. A conversation store enables the agent to persist
and recall message history across invocations.

### `InMemoryStore`

The built-in `InMemoryStore` keeps conversation history in process memory.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.conversation_store import InMemoryStore
from splunklib.ai.messages import HumanMessage
from splunklib.client import connect

model = OpenAIModel(...)
service = connect(...)

async with Agent(
    model=model,
    service=service,
    system_prompt="",
    conversation_store=InMemoryStore(),
) as agent:
    await agent.invoke([HumanMessage(content="Hi, my name is Chris.")])
    result = await agent.invoke([HumanMessage(content="What is my name?")])
    print(result.final_message.content)  # Chris
```

### Multiple conversation threads

Each conversation is isolated by a `thread_id`. You can pass a `thread_id` per invocation to maintain
separate histories for different users or sessions within the same agent instance.

```py
async with Agent(
    model=model,
    service=service,
    system_prompt="",
    conversation_store=InMemoryStore(),
) as agent:
    await agent.invoke(
        [HumanMessage(content="Hi, my name is Alice.")],
        thread_id="user-alice",
    )
    await agent.invoke(
        [HumanMessage(content="Hi, my name is Bob.")],
        thread_id="user-bob",
    )

    result = await agent.invoke(
        [HumanMessage(content="What is my name?")],
        thread_id="user-alice",
    )
    print(result.final_message.content)  # Alice - Bob's thread is unaffected
```

A custom `thread_id` can also be set on the agent constructor. When `invoke` is called without an explicit
`thread_id`, the `thread_id` from the constructor is used. If no `thread_id` is provided in the constructor, one
is generated implicitly.

```py
async with Agent(
    model=model,
    service=service,
    system_prompt="",
    conversation_store=InMemoryStore(),
    thread_id="session-42",
) as agent:
    await agent.invoke([HumanMessage(content="Hi, my name is Chris.")])

    # No thread_id supplied — falls back to "session-42"
    result = await agent.invoke([HumanMessage(content="What is my name?")])
    print(result.final_message.content)  # Chris
```

## Subagents

The `Agent` constructor can accept subagents as input parameters.

Subagents are specialized AI assistants designed to handle specific responsibilities. They help mitigate the **context bloat problem**
by breaking complex workflows into smaller, focused units instead of relying on a single, monolithic agent.
Each subagent can use a different model, allowing you to optimize for both capability and cost of specific operations.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.messages import HumanMessage
from splunklib.ai.tool_settings import LocalToolSettings, ToolAllowlist, ToolSettings
from splunklib.client import connect

model = OpenAIModel(...)
service = connect(...)

async with (
    Agent(
        model=highly_specialized_model,
        service=service,
        system_prompt=(
            "You are a highly specialized debugging agent, your job is to provide as much"
            "details as possible to resolve issues."
            "You have access to debugging-related tools, which you should leverage for your job."
        ),
        name="debugging_agent",
        description="Agent, that provided with logs will analyze and debug complex issues",
        tool_settings=ToolSettings(
            local=LocalToolSettings(allowlist=ToolAllowlist(tags=["debugging"])),
            remote=None,
        ),
    ) as debugging_agent,
    Agent(
        model=low_cost_model,
        service=service,
        system_prompt=(
            "You are a log analyzer agent. Your job is to query logs, based on the details that you receive and"
            "return a summary of interesting logs, that can be used for further analysis."
        ),
        name="log_analyzer_agent",
        description="Agent, that provided with a problem details will return logs, that could be related to the problem",
        tool_settings=ToolSettings(
            local=LocalToolSettings(allowlist=ToolAllowlist(tags=["spl"])),
            remote=None,
        ),
    ) as log_analyzer_agent,
):
    async with Agent(
        model=low_cost_model,
        service=service,
        system_prompt="You are a supervisor agent, use available subagents to perform requested operations.",
        agents=[debugging_agent, log_analyzer_agent],
    ) as agent:
        result = await agent.invoke(
            [
                HumanMessage(
                    content=(
                        "We are facing a production issue, users report that some pages do not exist, but it seems like the 404 are not deterministic."
                        "Query the logs in the index 'main', and try to debug the root cause of this issue."
                    ),
                )
            ]
        )
```

The supervisor agent relies on each subagent’s `name` and `description` to decide whether that subagent is appropriate
for a given task and should be called.

## Structured inputs and outputs

The input and output schemas are defined as `pydantic.BaseModel` classes and passed to the
`Agent` constructor via the `input_schema` and `output_schema` parameters.

## Subagents with ConversationStore

A subagent can be given its own `conversation_store`, enabling multi-turn conversations between
the supervisor and the subagent. When a subagent has a store, the supervisor can resume prior
conversations with a subagent.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.conversation_store import InMemoryStore
from splunklib.ai.messages import HumanMessage
from splunklib.client import connect

model = OpenAIModel(...)
service = connect(...)

async with (
    Agent(
        model=model,
        service=service,
        system_prompt=(
            "You are a log analysis expert. When asked to analyze a problem, "
            "ask clarifying questions if needed before querying logs."
        ),
        name="log_analyzer_agent",
        description="Analyzes logs and can ask follow-up questions to narrow down a problem.",
        conversation_store=InMemoryStore(),
    ) as log_analyzer_agent,
):
    async with Agent(
        model=model,
        service=service,
        system_prompt="You are a supervisor. Use the log analyzer agent to investigate issues.",
        agents=[log_analyzer_agent],
    ) as agent:
        # The supervisor calls the subagent and may continue the
        # same conversation with a subagent in the agentic loop and
        # across multiple agent loop invocations.
        await agent.invoke(...)
```

### Structured output

An `Agent` can be configured to return structured output. This allows applications to parse results deterministically
and perform programmatic reasoning without relying on free-form text.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.client import connect
from typing import Literal
from pydantic import BaseModel, Field

model = OpenAIModel(...)
service = connect(...)


class Output(BaseModel):
    service_name: str = Field(
        description="Name of the service or component where the failure occurred",
        min_length=1,
    )

    severity: Literal["critical", "high", "medium", "low", "info"] = Field(
        description="Assessed severity of the failure based on impact and urgency"
    )

    summary: str = Field(
        description="Concise human-readable summary of what went wrong",
        min_length=1,
    )


async with Agent(
    model=model,
    service=service,
    system_prompt="You are an agent, whose job is to determine the details of provided failure logs",
    output_schema=Output,
) as agent:
    # Use invoke_with_data when passing external data to the agent to reduce
    # the risk of prompt injection.
    result = await agent.invoke_with_data(
        instructions="Analyze this log and determine the failure details.",
        data=log,
    )

    # Make use of the output.
    result.structured_output.service_name
    result.structured_output.severity
    result.structured_output.summary
```

### Output schema generation details

When an `output_schema` is configured, the SDK automatically selects a strategy for generating
structured output based on the capabilities of the underlying model:

- **Provider strategy** - used when the model natively supports structured output.

- **Tool strategy** - used as a fallback when the model does not natively support structured outputs.
  The LLM passes the structured output into a tool call, according to the tool input schema. The
  tool schema corresponds to the `output_schema` pydantic model as passed to the `Agent` constructor.
  In that case the returned `AIMessage` will contain the `structured_output_calls` field populated
  and a `StructuredOutputMessage` will be appended to the message list, since each tool call must
  have a corresponding tool response.

The strategy is selected automatically - no configuration is required.

#### Output schema generation failure

Output schema generation can fail for various reasons:

- The model produces output that does not conform to the schema (e.g. wrong type, missing field,
  invalid enum value).
- The schema contains logic that cannot be fully expressed the encoded schema, which gets passed
  to the LLM - for example, a `model_validator`/`field_validator` that enforces a constraint.
  Because the model has no visibility into such constraints at generation time, it may produce
  values that pass schema validation but are then rejected by the validator at parse time.

  ```py
  class Output(BaseModel):
      min_score: float
      max_score: float = Field(description="max_score must be greater than min_score")

      @model_validator(mode="after")
      def max_must_exceed_min(self) -> "Output":
          if self.max_score <= self.min_score:
              raise ValueError("max_score must be greater than min_score")
          return self
  ```

- In case of **tool strategy** if the LLM model returned multiple structured output tool calls.

By default the output schema generation is re-tried, until the LLM generates a valid output.
This happens differently depending on the output schema generation strategy.

- **Provider strategy** - the validation error is fed back to the model, which is asked to
  regenerate the output in the same agentic loop iteration.
- **Tool strategy** - the validation error is returned as a tool response, prompting the model
  to retry the structured output tool call in the same agentic loop iteration.

On each failed attempt, a `StructuredOutputGenerationException` is raised inside the model
middleware chain. If the exception propagates out of the last middleware, the SDK catches it and
triggers the retry logic described above. A custom `model_middleware` can intercept this exception
to observe, log, or override the retry behavior. A custom `model_middleware` can also raise
the `StructuredOutputGenerationException` manually to reject structured output and force a re-generation.

The maximal number of re-tries is limited per agent loop invocation see [Default limits](#default-limits).

### Subagents with structured output/input

In addition to output schemas, subagents can define input schemas. These schemas both constrain
the inputs a subagent accepts and guide the supervisor agent by clearly specifying the expected
input structure.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.client import connect
from pydantic import BaseModel

model = OpenAIModel(...)
service = connect(...)


class Input(BaseModel): ...


class Output(BaseModel): ...


async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    name="...",
    description="...",
    input_schema=Input,
    output_schema=Output,
) as subagent:
    async with Agent(
        model=model,
        service=service,
        system_prompt="...",
        agents=[subagent],
    ) as agent:
        await agent.invoke(...)
```

> **Note**: Input schemas can only be used by subagents, not by regular agents. When invoking agents with external data, see [Security](#security) for guidance on how to do this safely.

> **Note**: Subagents with an `input_schema` receive their input via `invoke_with_data`, which separates instructions from data and reduces the risk of prompt injection. Subagents without an `input_schema` receive their input as a plain message, which provides weaker injection resistance - use them with caution when the supervisor may pass untrusted data.

## Middleware

Middleware lets you intercept model, tool, and subagent calls in a request/handler chain.
Each middleware can inspect input, call `handler(request)`, and modify the returned response.

Available decorators:

- `agent_middleware` - runs once per `invoke` call.
- `model_middleware` - runs on every model call.
- `tool_middleware` - runs on every tool call.
- `subagent_middleware` - runs on every subagent call.

Class-based middleware:

```py
from typing import Any, override
from splunklib.ai.messages import SubagentTextResult, ToolResult
from splunklib.ai.middleware import (
    AgentMiddleware,
    AgentMiddlewareHandler,
    AgentRequest,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
    SubagentMiddlewareHandler,
    SubagentRequest,
    SubagentResponse,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
)
from splunklib.ai.messages import AgentResponse, ToolCall


class ExampleMiddleware(AgentMiddleware):
    @override
    async def agent_middleware(
        self, request: AgentRequest, handler: AgentMiddlewareHandler
    ) -> AgentResponse[Any | None]:
        # Keep retrying until the agent makes at least one tool call.
        resp = await handler(request)
        while not any(m for m in resp.messages if isinstance(m, ToolCall)):
            resp = await handler(request)
        return resp

    @override
    async def model_middleware(
        self, request: ModelRequest, handler: ModelMiddlewareHandler
    ) -> ModelResponse:
        return await handler(
            ModelRequest(
                system_message=request.system_message.replace("SECRET", "[REDACTED]"),
                state=request.state,
            )
        )

    @override
    async def tool_middleware(
        self, request: ToolRequest, handler: ToolMiddlewareHandler
    ) -> ToolResponse:
        if request.call.name == "temperature":
            return ToolResponse(result=ToolResult(content="25.0", structured_content=None))
        return await handler(request)

    @override
    async def subagent_middleware(
        self, request: SubagentRequest, handler: SubagentMiddlewareHandler
    ) -> SubagentResponse:
        if request.call.name == "SummaryAgent":
            return SubagentResponse(
                result=SubagentTextResult(
                    content="Executive summary: no critical incidents detected."
                )
            )
        return await handler(request)
```

Example agent middleware:

```py
from typing import Any
from splunklib.ai.middleware import (
    agent_middleware,
    AgentMiddlewareHandler,
    AgentRequest,
)
from splunklib.ai.messages import AgentResponse, ToolCall


@agent_middleware
async def force_tool_call(
    request: AgentRequest, handler: AgentMiddlewareHandler
) -> AgentResponse[Any | None]:
    # Keep retrying until the agent makes at least one tool call.
    resp = await handler(request)
    while not any(m for m in resp.messages if isinstance(m, ToolCall)):
        resp = await handler(request)
    return resp
```

Example model middleware:

```py
from splunklib.ai.middleware import (
    model_middleware,
    ModelMiddlewareHandler,
    ModelRequest,
    ModelResponse,
)


@model_middleware
async def redact_system_prompt(
    request: ModelRequest, handler: ModelMiddlewareHandler
) -> ModelResponse:
    return await handler(
        ModelRequest(
            system_message=request.system_message.replace("SECRET", "[REDACTED]"),
            state=request.state,
        )
    )
```

Example tool middleware:

```py
from splunklib.ai.middleware import (
    tool_middleware,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
)


@tool_middleware
async def mock_temperature(request: ToolRequest, handler: ToolMiddlewareHandler) -> ToolResponse:
    if request.call.name == "temperature":
        return ToolResponse(result=ToolResult(content="25.0", structured_content=None))
    return await handler(request)
```

Example subagent middleware:

```py
from splunklib.ai.messages import SubagentTextResult
from splunklib.ai.middleware import (
    subagent_middleware,
    SubagentMiddlewareHandler,
    SubagentRequest,
    SubagentResponse,
)


@subagent_middleware
async def mock_subagent(
    request: SubagentRequest, handler: SubagentMiddlewareHandler
) -> SubagentResponse:
    if request.call.name == "SummaryAgent":
        return SubagentResponse(
            result=SubagentTextResult(content="Executive summary: no critical incidents detected.")
        )
    return await handler(request)
```

Retry pattern (bounded retries):

```py
from splunklib.ai.middleware import (
    tool_middleware,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
)


class RetryableToolError(Exception):
    pass


@tool_middleware
async def retry_transient_tool_failures(
    request: ToolRequest, handler: ToolMiddlewareHandler
) -> ToolResponse:
    last_error: Exception | None = None
    for _ in range(3):
        try:
            return await handler(request)
        except RetryableToolError as e:
            last_error = e

    assert last_error is not None
    raise last_error
```

Pass middleware to `Agent`:

```py
async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    middleware=[redact_system_prompt, mock_temperature, mock_subagent],
) as agent:
    ...
```

## Hooks

Hooks are user-defined callback functions that can be registered to execute at specific points
during the agent's operation. Hooks allow developers to add custom behavior, logging and monitoring
or implement custom stopping conditions for the agent loop without modifying the core agent logic.

There are several types of hooks available.
They differ by the point in the execution flow where they are invoked:

- before_model: before each model call
- after_model: after each model call
- before_agent: once per agent invocation, before any model calls
- after_agent: once per agent invocation, after all model calls

Hooks implement the same interface as middlewares, which allows them to be supplied
directly as middleware instances in the Agent constructor.

Example hook that logs token usage after each model call:

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.ai.hooks import before_model
from splunklib.ai.middleware import ModelRequest
from splunklib.client import connect

import logging

logger = logging.getLogger(__name__)

model = OpenAIModel(...)
service = connect(...)


@before_model
def log_steps(req: ModelRequest) -> None:
    logger.debug(f"Steps: {len(req.state.messages)}")


async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    middleware=[log_steps],
) as agent:
    ...
```

The hooks can stop the Agentic Loop under custom conditions by raising exceptions, for example:

```py
from splunklib.ai.hooks import before_model
from splunklib.ai.middleware import AgentMiddleware, ModelRequest


def message_limit(message_limit: int) -> AgentMiddleware:
    @before_model
    def _hook(req: ModelRequest) -> None:
        if len(req.state.messages) >= message_limit:
            raise Exception("Stopping Agentic Loop")

    return _hook


async with Agent(
    ...,
    middleware=[message_limit(message_limit=5)],
) as agent:
    ...
```

## Default limits

Every `Agent` automatically applies sane default limits to prevent runaway execution
or excessive token usage.

| Limit | Default | Measured |
|---|---|---|
| `max_tokens` | 200 000 tokens | token count of messages passed to the model |
| `max_steps` | 100 steps | number of messages in the conversation |
| `timeout` | 600 seconds (10 minutes) | per `invoke` call |
| `max_structured_output_retires` | 3 retries | per `invoke` call |

`max_tokens` and `max_steps` are checked against the messages passed to the model on each call.
`timeout` and `max_structured_output_retires` reset on each `invoke`, so they limit only the
current agent loop invocation.

When a limit is exceeded, the agent raises the corresponding exception:
`TokenLimitExceededException`, `StepsLimitExceededException`, `TimeoutExceededException`, or
`StructuredOutputRetryLimitExceededException`.

### Overriding defaults

Limits are configured via the `AgentLimits` dataclass passed to the `Agent` constructor.
Only the fields you specify are overridden; the rest keep their defaults:

```py
from splunklib.ai.limits import AgentLimits

async with Agent(
    ...,
    limits=AgentLimits(max_tokens=50_000),  # overrides default 200 000; other defaults still apply
) as agent:
    ...
```

To override all defaults:

```py
async with Agent(
    ...,
    limits=AgentLimits(
        max_tokens=50_000,
        max_steps=10,
        timeout=30.0,
        max_structured_output_retires=0,  # no retries
    ),
) as agent:
    ...
```

There is no explicit opt-out - the intent is that agents should always have some guardrails.

## Logger

The `Agent` constructor accepts an optional logger parameter that enables detailed
tracing and debugging throughout the agent’s lifecycle.

```py
from splunklib.ai import Agent, OpenAIModel
from splunklib.client import connect
import logging

model = OpenAIModel(...)
service = connect(...)

logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    logger=logger,
) as agent:
    ...
```

The agent emits logs for events such as: model interactions, tool calls, subagent calls.

Additionally logs from local tools are also forwarded to this logger.

## Security

The SDK provides layered, automatic defenses and opt-in utilities to help you build secure
agentic applications. Automatic protections are active for every agent with no configuration
required. Opt-in utilities give you additional control where your use case requires it.

### What's on by default

| Protection | Default |
|---|---|
| Token limit | 200 000 tokens |
| Step limit | 100 steps |
| Timeout | 600 seconds per `invoke` |
| System prompt hardening | Automatic - security rules are appended to every agent's system prompt |

See [Overriding defaults](#overriding-defaults) to customize or override these limits.

### Prompt injection

The SDK automatically appends injection-resistance rules to every agent's system prompt, so you
do not need to add them manually. For additional protection when passing external or user-supplied
data into the agent, use `invoke_with_data` instead of `invoke`. It separates your instructions
from the untrusted data, reducing the risk of prompt injection:

```py
from splunklib.ai.messages import HumanMessage

# Use invoke for plain conversational messages.
result = await agent.invoke([HumanMessage(content="What are the top threats this week?")])

# Use invoke_with_data when passing external data to the agent.
result = await agent.invoke_with_data(
    instructions="Summarize this security alert and assess its severity.",
    data=alert_payload,  # str or dict
)
```

If you prefer to build the message manually, `create_structured_prompt` gives you the same
separation and can be used directly inside a `HumanMessage`:

```py
from splunklib.ai import create_structured_prompt
from splunklib.ai.messages import HumanMessage

result = await agent.invoke(
    [
        HumanMessage(
            content=create_structured_prompt(
                instructions="Summarize this security alert and assess its severity.",
                data=alert_payload,
            )
        )
    ]
)
```

For additional opt-in protection, the SDK provides `truncate_input` and `detect_injection`.
`truncate_input` caps the input length inline when constructing a message. `detect_injection`
scans for common injection patterns - one way to apply it consistently is via `agent_middleware`,
which gives you a single place to enforce the policy across every `invoke()` call. You decide
what to do when injection is detected:

```py
from typing import Any
from splunklib.ai import Agent, OpenAIModel, detect_injection, truncate_input
from splunklib.ai.middleware import (
    agent_middleware,
    AgentMiddlewareHandler,
    AgentRequest,
)
from splunklib.ai.messages import AgentResponse, HumanMessage


@agent_middleware
async def injection_guard(
    request: AgentRequest, handler: AgentMiddlewareHandler
) -> AgentResponse[Any | None]:
    for msg in request.messages:
        if isinstance(msg, HumanMessage) and detect_injection(msg.content):
            raise ValueError("Potential prompt injection detected in input.")
    return await handler(request)


async with Agent(
    model=model,
    service=service,
    system_prompt="...",
    middleware=[injection_guard],
) as agent:
    await agent.invoke([HumanMessage(content=truncate_input(user_input))])
```

### Tool and subagent results

Tool results and subagent responses are delivered to the LLM using the `tool` message role,
which models recognize as data rather than instructions. In addition, the SDK automatically
appends security rules to every agent's system prompt instructing the LLM to treat all tool
and subagent results as data to analyze, not commands to execute.

Subagents are internally represented as tools - their responses go through the same `tool`
message role and are covered by the same system prompt rules.

These defenses significantly reduce the risk of indirect prompt injection through results,
but they are not a 100% guarantee. Developers should:

- Use models that reliably respect message roles and system prompt instructions
- Validate or sanitize results from external systems before passing them through tools or subagents
- Apply the principle of least privilege - the fewer tools an agent has, the smaller the
  attack surface if a result is adversarial

### Audit logging

The SDK's built-in logger (see [Logger](#logger)) emits structured debug events for tool calls,
subagent calls, and model interactions. These events include tool names, call IDs, and
success/failure status - metadata only, never message content.

When adding custom logging via middleware or hooks, avoid logging message content or any data
that may contain sensitive information or PII. Log metadata instead:

```py
from splunklib.ai.middleware import (
    tool_middleware,
    ToolMiddlewareHandler,
    ToolRequest,
    ToolResponse,
)


@tool_middleware
async def audit_tool_calls(request: ToolRequest, handler: ToolMiddlewareHandler) -> ToolResponse:
    logger.info("tool_call started", extra={"tool": request.call.name})
    return await handler(request)
```

### Developer responsibility

The SDK provides structural guardrails, but cannot enforce every security rule for every use
case. As the application developer, you are responsible for the data that flows through your
application and into the LLM.

We recommend that you:

- Audit which data sources feed into `invoke` / `invoke_with_data` and verify that no
  sensitive data is included unintentionally
- Use the logger and middleware to observe agent behavior during development and confirm
  that data flows match your expectations
- Choose an LLM provider appropriate for your data sensitivity requirements - for example,
  a self-hosted model for highly sensitive or regulated data

### Further reading

For a comprehensive overview of LLM-specific risks, see the
[OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## Known issues

### CA - File not found

If you encounter an exception indicating that CA certificates are missing (for example, a “file does not exist” error),
add the following snippet to your code:

```py
CA_TRUST_STORE = "/opt/splunk/openssl/cert.pem"
if os.environ.get("SSL_CERT_FILE") == CA_TRUST_STORE and not os.path.exists(CA_TRUST_STORE):
    os.environ["SSL_CERT_FILE"] = ""
```

This causes the system CAs to be used instead of the ones from the `SSL_CERT_FILE`, which might not exist for reasons.

### AppInspect

Currently when the App that uses `splunk-sdk[openai]` is installed on Splunk Cloud, AppInspect can flag some of the
files from the dependency package.

The files that get flagged are:

- `openai/lib/.keep`
- `openai/helpers/microphone.py`

As a workaround, both of those files are not required for the App to work and can be excluded when packaging the App:

```sh
gtar --transform='s,^,<your_app>/,' \
  --exclude="__pycache__" \
  --exclude=".keep" \
  --exclude="bin/lib/openai/helpers/microphone.py" \
  -czf dist/<your_app>.tgz \
  bin default
```
