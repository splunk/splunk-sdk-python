import logging

mcp_package_name = "splunklib.mcp"

# <https://packaging.python.org/en/latest/guides/packaging-namespace-packages/>
try:
    __import__(mcp_package_name)

except ModuleNotFoundError as mnfe:
    logging.error("Tried to import splunk-sdk-mcp without installing int", mnfe)

    raise ModuleNotFoundError(
        "PLease install splunk-sdk-mcp package to use these features."
    ) from mnfe
