import sys
import splunklib
from .metric import Metric, MetricType
from .sender import TelemetrySender

import logging
from splunklib import setup_logging

setup_logging(logging.DEBUG)

log = logging.getLogger()

SDK_USAGE_COMPONENT = "splunk.sdk.usage"


# FIXME: adding Service typehint produces circular dependency
def log_telemetry_sdk_usage(service, **kwargs):
    metric = Metric(
        MetricType.Event,
        SDK_USAGE_COMPONENT,
        {
            "sdk-language": "python",
            "python-version": sys.version,
            "sdk-version": splunklib.__version__,
            **kwargs,
        },
        4,
    ) 
    try:
        log.debug(f"sending new telemetry {metric}")
        telemetry = TelemetrySender(service)
        # TODO: handle possible errors
        _, _ = telemetry.send(metric)
    except Exception as e:
        log.error("Could not send telemetry", exc_info=True)
