# Copyright 2011-2013 Splunk, Inc.
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

from logging.config import fileConfig
import os
import sys

_script_directory = os.path.dirname(sys.argv[0])
_app_directory = os.path.dirname(os.path.abspath(_script_directory))


def configure(path=None):
    """ Read logging configuration from the logging.conf file, if it exists

    This function expects a Splunk application directory structure:

        <app-root>
            bin
                <custom-search-command>.py
                ...
            default
                logging.conf
                ...
            local
                logging.conf
                ...

    The **logging.conf** file must be in ConfigParser-format. The current
    working directory is set to *<app-root>* before the logging.conf file is
    loaded. Hence, relative path names should be set relative to *<app-root>*.

    The current directory is reset to its previous value before this function
    returns.

    """
    if path is None:
        for relative_path in 'local/logging.conf', 'default/logging.conf':
            configuration_file = os.path.join(_app_directory, relative_path)
            if os.path.exists(configuration_file):
                path = configuration_file
                break
    if path is not None:
        working_directory = os.getcwd()
        os.chdir(_app_directory)
        try:
            fileConfig(path)
        finally:
            os.chdir(working_directory)
