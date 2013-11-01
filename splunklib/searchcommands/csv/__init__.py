# Copyright 2011-2012 Splunk, Inc.
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

from __future__ import absolute_import
import csv

from . DictReader import DictReader
from . DictWriter import DictWriter


# TODO: Data conversion:
# + What is the set of data types native to Splunk?
# + We process lists. We know about boolean, numeric, and fieldname (a kind of
#   string identity type), but how do we read/write the others, whatever they
#   happen to be?
from . import Dialect

__version_info__ = (0, 8, 0)
__version__ = ".".join(map(str, __version_info__))

# Set the maximum allowable CSV field size
#
# The default of the csv module is 128KB; upping to 10MB. See SPL-12117 for
# the background on issues surrounding field sizes.
csv.field_size_limit(10485760)
