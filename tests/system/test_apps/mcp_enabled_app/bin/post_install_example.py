from splunklib.mcp import tools


async def post_install(splunk_url: str, auth_token: str) -> None:
    # TODO: Implement
    try:
        await tools.register_tools_from(["./tools.py", "../local/ai.conf"])
    except Exception as e:
        print(e)
        raise e
