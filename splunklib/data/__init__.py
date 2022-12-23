# Copyright 2011-2015 Splunk, Inc.
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

"""The **splunklib.data** module reads the responses from splunkd in Atom Feed
format, which is the format used by most of the REST API.
"""

from .Record import Record


def record(value=None):
    """This function returns a :class:`Record` instance constructed with an
    initial value that you provide.

    :param value: An initial record value.
    :type value: ``dict``
    """
    if value is None:
        value = {}
    return Record(value)
