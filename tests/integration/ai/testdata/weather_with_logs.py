from splunklib.ai.registry import ToolContext, ToolRegistry

registry = ToolRegistry()


@registry.tool(description="Returns the current temperature in the city")
def temperature(ctx: ToolContext, city: str) -> str:
    ctx.logger.debug("debug log")
    ctx.logger.info("info log")
    ctx.logger.warning("warning log")
    ctx.logger.error("error log")
    ctx.logger.critical("critical log")

    if city == "Krakow":
        return "31.5C"
    else:
        return "22.1C"


registry.run()
