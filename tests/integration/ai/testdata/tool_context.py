from splunklib.ai.registry import ToolContext, ToolRegistry

registry = ToolRegistry()


@registry.tool(description="Returns the startup time of the splunk instance")
def startup_time(ctx: ToolContext) -> str:
    return f"{ctx.service.info.startup_time}"


@registry.tool(
    description="Returns the startup time of the splunk instance appended to a value"
)
def startup_time_and_str(ctx: ToolContext, val: str) -> str:
    return f"{val} {ctx.service.info.startup_time}"


registry.run()
