import logging

from splunklib.ai.registry import ToolContext, ToolRegistry

registry = ToolRegistry()


@registry.tool()
async def hello(ctx: ToolContext, name: str) -> str:
    ctx.logger.debug(msg="debug log")
    ctx.logger.info(msg="info log")
    ctx.logger.warning(msg="warning log")
    ctx.logger.error(msg="error log")
    ctx.logger.critical(msg="critical log")

    ctx.logger.log(level=logging.DEBUG - 1, msg="debug-1 log")
    ctx.logger.log(level=logging.INFO - 1, msg="info-1 log")
    ctx.logger.log(level=logging.WARN - 1, msg="warn-1 log")
    ctx.logger.log(level=logging.ERROR - 1, msg="error-1 log")
    ctx.logger.log(level=logging.CRITICAL - 1, msg="critical-1 log")

    ctx.logger.log(level=logging.NOTSET + 1, msg="notset+1 log")
    ctx.logger.log(level=logging.DEBUG + 1, msg="debug+1 log")
    ctx.logger.log(level=logging.INFO + 1, msg="info+1 log")
    ctx.logger.log(level=logging.WARN + 1, msg="warn+1 log")
    ctx.logger.log(level=logging.ERROR + 1, msg="error+1 log")
    ctx.logger.log(level=logging.CRITICAL + 1, msg="critical+1 log")

    return f"Hello {name}"


registry.run()
