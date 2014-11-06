# Copyright 2011-2014 Splunk, Inc.
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
from logging import getLogger, root, StreamHandler
import os
import sys

def get_app_directory(probing_path):
    return os.path.dirname(os.path.abspath(os.path.dirname(probing_path)))

def configure(name, probing_path=None, app_root=None):
    """ Configure logging and return a logger and the location of its logging
    configuration file.

    This function expects:

    + A Splunk app directory structure::

        <app-root>
            bin
                ...
            default
                ...
            local
                ...

    + The current working directory is *<app-root>***/bin**.

      Splunk guarantees this. If you are running the app outside of Splunk, be
      sure to set the current working directory to *<app-root>***/bin** before
      calling.

    This function looks for a logging configuration file at each of these
    locations, loading the first, if any, logging configuration file that it
    finds::

        local/{name}.logging.conf
        default/{name}.logging.conf
        local/logging.conf
        default/logging.conf

    The current working directory is set to *<app-root>* before the logging
    configuration file is loaded. Hence, paths in the logging configuration
    file are relative to *<app-root>*. The current directory is reset before
    return.

    You may short circuit the search for a logging configuration file by
    providing an alternative file location in `probing_path`. Logging configuration
    files must be in `ConfigParser format`_.

    #Arguments:

    :param name: Logger name
    :type name: str
    :param probing_path: Location of an alternative logging configuration file or `None`
    :type probing_path: str or NoneType
    :returns: A logger and the location of its logging configuration file
    :param app_root: The root of the application directory, used primarily by tests.
    :type app_root: str or NoneType

    .. _ConfigParser format: http://goo.gl/K6edZ8

    """

    app_directory = get_app_directory(sys.argv[0]) if app_root is None else app_root

    if probing_path is None:
        probing_paths = [
            'local/%s.logging.conf' % name,
            'default/%s.logging.conf' % name,
            'local/logging.conf',
            'default/logging.conf']
        for relative_path in probing_paths:
            configuration_file = os.path.join(app_directory, relative_path)
            if os.path.exists(configuration_file):
                probing_path = configuration_file
                break
    elif not os.path.isabs(probing_path):
        found = False
        for conf in 'local', 'default':
            configuration_file = os.path.join(app_directory, conf, probing_path)
            if os.path.exists(configuration_file):
                probing_path = configuration_file
                found = True
                break
        if not found:
            raise ValueError(
                'Logging configuration file "%s" not found in local or default '
                'directory' % probing_path)
    elif not os.path.exists(probing_path):
        raise ValueError('Logging configuration file "%s" not found')

    if probing_path is not None:
        working_directory = os.getcwd()
        os.chdir(app_directory)
        try:
            splunk_home = os.path.normpath(os.path.join(working_directory, os.environ['SPLUNK_HOME']))
        except KeyError:
            splunk_home = working_directory  # reasonable in debug scenarios
        try:
            probing_path = os.path.abspath(probing_path)
            fileConfig(probing_path, {'SPLUNK_HOME': splunk_home})
        finally:
            os.chdir(working_directory)

    if len(root.handlers) == 0:
        root.addHandler(StreamHandler())

    logger = getLogger(name)
    return logger, probing_path
