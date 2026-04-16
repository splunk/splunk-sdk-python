from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()

count = 0


@registry.tool()
def backdoor_tool_call_count() -> int:
    return count


@registry.tool(description="Returns the current temperature in the city")
def temperature(city: str) -> str:
    global count
    count += 1

    if city == "Krakow":
        return "31.5C"
    elif city == "Warsaw":
        return "30.0C"
    elif city == "Gdansk":
        return "25.5C"
    elif city == "Poznan":
        return "28.5C"
    else:
        return "22.1C"


registry.run()
