# Copyright © 2011-2024 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python library for Splunk."""

import logging

try:
    import importlib.metadata as importlib
except (ImportError, ModuleNotFoundError):
    # For Python < 3.8, use importlib_metadata backport
    import importlib_metadata as importlib

DEFAULT_LOG_FORMAT = (
    "%(asctime)s, Level=%(levelname)s, Pid=%(process)s, Logger=%(name)s, File=%(filename)s, "
    "Line=%(lineno)s, %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


# To set the logging level of splunklib
# ex. To enable debug logs, call this method with parameter 'logging.DEBUG'
# default logging level is set to 'WARNING'
def setup_logging(
    level, log_format=DEFAULT_LOG_FORMAT, date_format=DEFAULT_DATE_FORMAT
):
    logging.basicConfig(level=level, format=log_format, datefmt=date_format)


__version__ = importlib.version("splunk-sdk")
