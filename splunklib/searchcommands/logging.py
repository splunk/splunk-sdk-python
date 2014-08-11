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


def configure(name, path=None):
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
    providing an alternative file location in `path`. Logging configuration
    files must be in `ConfigParser format`_.

    #Arguments:

    :param name: Logger name
    :type name: str
    :param path: Location of an alternative logging configuration file or `None`
    :type path: str or NoneType
    :returns: A logger and the location of its logging configuration file

    .. _ConfigParser format: http://goo.gl/K6edZ8

    """
    app_directory = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

    if path is None:
        probing_path = [
            'local/%s.logging.conf' % name,
            'default/%s.logging.conf' % name,
            'local/logging.conf',
            'default/logging.conf']
        for relative_path in probing_path:
            configuration_file = os.path.join(app_directory, relative_path)
            if os.path.exists(configuration_file):
                path = configuration_file
                break
    elif not os.path.isabs(path):
        found = False
        for conf in 'local', 'default':
            configuration_file = os.path.join(app_directory, conf, path)
            if os.path.exists(configuration_file):
                path = configuration_file
                found = True
                break
        if not found:
            raise ValueError(
                'Logging configuration file "%s" not found in local or default '
                'directory' % path)
    elif not os.path.exists(path):
        raise ValueError('Logging configuration file "%s" not found')

    if path is not None:
        working_directory = os.getcwd()
        os.chdir(app_directory)
        try:
            splunk_home = os.path.normpath(os.path.join(working_directory, os.environ['SPLUNK_HOME']))
        except KeyError:
            splunk_home = working_directory  # reasonable in debug scenarios
        try:
            path = os.path.abspath(path)
            fileConfig(path, {'SPLUNK_HOME': splunk_home})
        finally:
            os.chdir(working_directory)

    if len(root.handlers) == 0:
        root.addHandler(StreamHandler())

    logger = getLogger(name)
    return logger, path
