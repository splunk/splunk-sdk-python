splunklib.ai
------------

.. automodule:: splunklib.ai

.. autoclass:: splunklib.ai.agent.Agent
    :members: invoke, invoke_with_data

.. autoexception:: splunklib.ai.agent.PrivilegedExecutionError
    :members:

.. rubric:: Models

.. autoclass:: splunklib.ai.model.PredefinedModel
    :members:

.. autoclass:: splunklib.ai.model.AnthropicModel
    :members:

.. autoclass:: splunklib.ai.model.OpenAIModel
    :members:

.. autoclass:: splunklib.ai.model.GoogleModel
    :members:

.. rubric:: Messages

.. autoclass:: splunklib.ai.messages.BaseMessage
    :members:

.. autoclass:: splunklib.ai.messages.HumanMessage
    :members:

.. autoclass:: splunklib.ai.messages.AIMessage
    :members:

.. autoclass:: splunklib.ai.messages.SystemMessage
    :members:

.. autoclass:: splunklib.ai.messages.ToolMessage
    :members:

.. autoclass:: splunklib.ai.messages.SubagentMessage
    :members:

.. autoclass:: splunklib.ai.messages.AgentResponse
    :members:

.. autoclass:: splunklib.ai.messages.TextBlock
    :members:

.. autoclass:: splunklib.ai.messages.ToolCall
    :members:

.. autoclass:: splunklib.ai.messages.SubagentCall
    :members:

.. autoclass:: splunklib.ai.messages.ToolResult
    :members:

.. autoclass:: splunklib.ai.messages.SubagentTextResult
    :members:

.. autoclass:: splunklib.ai.messages.SubagentStructuredResult
    :members:

.. autoclass:: splunklib.ai.messages.ToolFailureResult
    :members:

.. autoclass:: splunklib.ai.messages.SubagentFailureResult
    :members:

.. rubric:: Middleware

.. autoclass:: splunklib.ai.middleware.AgentMiddleware
    :members:

.. autofunction:: splunklib.ai.middleware.agent_middleware

.. autofunction:: splunklib.ai.middleware.model_middleware

.. autofunction:: splunklib.ai.middleware.tool_middleware

.. autofunction:: splunklib.ai.middleware.subagent_middleware

.. autoclass:: splunklib.ai.middleware.AgentState
    :members:

.. autoclass:: splunklib.ai.middleware.AgentRequest
    :members:

.. autoclass:: splunklib.ai.middleware.ModelRequest
    :members:

.. autoclass:: splunklib.ai.middleware.ModelResponse
    :members:

.. autoclass:: splunklib.ai.middleware.ToolRequest
    :members:

.. autoclass:: splunklib.ai.middleware.ToolResponse
    :members:

.. autoclass:: splunklib.ai.middleware.SubagentRequest
    :members:

.. autoclass:: splunklib.ai.middleware.SubagentResponse
    :members:

.. rubric:: Limits

.. autoclass:: splunklib.ai.limits.AgentLimits
    :members:

.. autoexception:: splunklib.ai.limits.AgentStopException
    :members:

.. autoexception:: splunklib.ai.limits.TokenLimitExceededException
    :members:

.. autoexception:: splunklib.ai.limits.StepsLimitExceededException
    :members:

.. autoexception:: splunklib.ai.limits.TimeoutExceededException
    :members:

.. autoexception:: splunklib.ai.limits.StructuredOutputRetryLimitExceededException
    :members:

.. rubric:: Tool settings

.. autoclass:: splunklib.ai.tool_settings.ToolSettings
    :members:

.. autoclass:: splunklib.ai.tool_settings.LocalToolSettings
    :members:

.. autoclass:: splunklib.ai.tool_settings.RemoteToolSettings
    :members:

.. autoclass:: splunklib.ai.tool_settings.ToolAllowlist
    :members:

.. rubric:: Conversation store

.. autoclass:: splunklib.ai.conversation_store.ConversationStore
    :members:

.. autoclass:: splunklib.ai.conversation_store.InMemoryStore
    :members:

.. rubric:: Security

.. autofunction:: splunklib.ai.security.detect_injection

.. autofunction:: splunklib.ai.security.truncate_input

.. autofunction:: splunklib.ai.security.create_structured_prompt
