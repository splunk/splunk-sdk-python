from splunklib.ai.registry import ToolRegistry

registry = ToolRegistry()


@registry.tool(description="Returns the current temperature in the city")
def temperature(city: str) -> str:
    if city == "Krakow":
        return "31.5C"
    else:
        return "22.1C"


registry.run()
