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
from logging import getLogger
import inspect
import os


def configure(cls, path=None):
    """ Configure logging for the app containing a class and get its logger

    This function expects a Splunk app directory structure:

        <app-root>
            bin
                <module>.py
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

    #Arguments:

    :param cls: Class contained in <app-root>/bin/<module>.py
    :type cls: type
    :param path: Location of an alternative logging configuration file or `None`
    :type path: str or NoneType

    """
    logger_name = cls.__name__
    module = inspect.getmodule(cls)
    app_directory = os.path.dirname(os.path.dirname(module.__file__))
    if path is None:
        probing_path = [
            'local/%s.logging.conf' % logger_name,
            'default/%s.logging.conf' % logger_name,
            'local/logging.conf',
            'default/logging.conf']
        for relative_path in probing_path:
            configuration_file = os.path.join(app_directory, relative_path)
            if os.path.exists(configuration_file):
                path = configuration_file
                break
    if path is not None:
        working_directory = os.getcwd()
        os.chdir(app_directory)
        try:
            path = os.path.abspath(path)
            fileConfig(path)
        finally:
            os.chdir(working_directory)
    logger = getLogger(logger_name)
    return logger, path
