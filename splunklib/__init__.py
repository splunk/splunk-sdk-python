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

"""Splunk Software Development Kit for Python"""

import logging

DEFAULT_LOG_FORMAT = (
    "%(asctime)s, Level=%(levelname)s, Pid=%(process)s, Logger=%(name)s, File=%(filename)s, "
    "Line=%(lineno)s, %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


def setup_logging(
    level: int = logging.WARNING,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    force: bool = False,
) -> None:
    """Enable logs from splunklib"""
    logging.basicConfig(
        level=level, format=log_format, datefmt=date_format, force=force
    )


setup_logging(level=logging.DEBUG, force=True)


__VERSION_SEMVER__ = (2, 2, 0, "alpha")
__VERSION__ = ".".join(map(str, __VERSION_SEMVER__))
