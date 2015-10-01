#!/usr/bin/env python
#
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

"""Shared unit test utilities."""
import contextlib

import sys
# Run the test suite on the SDK without installing it.
sys.path.insert(0, '../')
sys.path.insert(0, '../examples')

import splunklib.client as client
from time import sleep
from datetime import datetime, timedelta
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

import os
import time

import logging
logging.basicConfig(
    filename='test.log',
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s")

class NoRestartRequiredError(Exception):
    pass

class WaitTimedOutError(Exception):
    pass

def to_bool(x):
    if x == '1':
        return True
    elif x == '0':
        return False
    else:
        raise ValueError("Not a boolean value: %s", x)


def tmpname():
    name = 'delete-me-' + str(os.getpid()) + str(time.time()).replace('.','-')
    return name


def wait(predicate, timeout=60, pause_time=0.5):
    assert pause_time < timeout
    start = datetime.now()
    diff = timedelta(seconds=timeout)
    while not predicate():
        if datetime.now() - start > diff:
            logging.debug("wait timed out after %d seconds", timeout)
            raise WaitTimedOutError
        sleep(pause_time)
        logging.debug("wait finished after %s seconds", datetime.now()-start)


class SDKTestCase(unittest.TestCase):
    restart_already_required = False
    installedApps = []

    def assertEventuallyTrue(self, predicate, timeout=10, pause_time=0.5,
                             timeout_message="Operation timed out."):
        assert pause_time < timeout
        start = datetime.now()
        diff = timedelta(seconds=timeout)
        while not predicate():
            if datetime.now() - start > diff:
                logging.debug("wait timed out after %d seconds", timeout)
                self.fail(timeout_message)
            sleep(pause_time)
            logging.debug("wait finished after %s seconds", datetime.now()-start)

    def check_content(self, entity, **kwargs):
        for k, v in kwargs.iteritems(): 
            self.assertEqual(entity[k], str(v))

    def check_entity(self, entity):
        assert entity is not None
        self.assertTrue(entity.name is not None)
        self.assertTrue(entity.path is not None)

        self.assertTrue(entity.state is not None)
        self.assertTrue(entity.content is not None)

        # Verify access metadata
        assert entity.access is not None
        entity.access.app
        entity.access.owner
        entity.access.sharing

        # Verify content metadata

        # In some cases, the REST API does not return field metadata for when
        # entities are intially listed by a collection, so we refresh to make
        # sure the metadata is available.
        entity.refresh()

        self.assertTrue(isinstance(entity.fields.required, list))
        self.assertTrue(isinstance(entity.fields.optional, list))
        self.assertTrue(isinstance(entity.fields.wildcard, list))

        # Verify that all required fields appear in entity content

        for field in entity.fields.required:
            try:
                self.assertTrue(field in entity.content)
            except:
                # Check for known exceptions
                if "configs/conf-times" in entity.path:
                    if field in ["is_sub_menu"]:
                        continue
                raise

    def clear_restart_message(self):
        """Tell Splunk to forget that it needs to be restarted.

        This is used mostly in cases such as deleting a temporary application.
        Splunk asks to be restarted when that happens, but unless the application
        contained modular input kinds or the like, it isn't necessary.
        """
        if not self.service.restart_required:
            raise ValueError("Tried to clear restart message when there was none.")
        try:
            self.service.delete("messages/restart_required")
        except client.HTTPError as he:
            if he.status == 404:
                pass
            else:
                raise

    @contextlib.contextmanager
    def fake_splunk_version(self, version):
        original_version = self.service.splunk_version
        try:
            self.service._splunk_version = version
            yield
        finally:
            self.service._splunk_version = original_version


    def install_app_from_collection(self, name):
        collectionName = 'sdk-app-collection'
        if collectionName not in self.service.apps:
            raise ValueError("sdk-test-application not installed in splunkd")
        appPath = self.pathInApp(collectionName, ["build", name+".tar"])
        kwargs = {"update": 1, "name": appPath}
        try:
            self.service.post("apps/appinstall", **kwargs)
        except client.HTTPError as he:
            if he.status == 400:
                raise IOError("App %s not found in app collection" % name)
        if self.service.restart_required:
            self.service.restart(120)
        self.installedApps.append(name)

    def app_collection_installed(self):
        collectionName = 'sdk-app-collection'
        return collectionName in self.service.apps

    def pathInApp(self, appName, pathComponents):
        """Return a path to *pathComponents* in *appName*.

        `pathInApp` is used to refer to files in applications installed with
        `install_app_from_collection`. For example, the app `file_to_upload` in
        the collection contains `log.txt`. To get the path to it, call::

            pathInApp('file_to_upload', ['log.txt'])

        The path to `setup.xml` in `has_setup_xml` would be fetched with::

            pathInApp('has_setup_xml', ['default', 'setup.xml'])

        `pathInApp` figures out the correct separator to use (based on whether
        splunkd is running on Windows or Unix) and joins the elements in
        *pathComponents* into a path relative to the application specified by
        *appName*.

        *pathComponents* should be a list of strings giving the components.
        This function will try to figure out the correct separator (/ or \)
        for the platform that splunkd is running on and construct the path
        as needed.

        :return: A string giving the path.
        """
        splunkHome = self.service.settings['SPLUNK_HOME']
        if "\\" in splunkHome:
            # This clause must come first, since Windows machines may
            # have mixed \ and / in their paths.
            separator = "\\"
        elif "/" in splunkHome:
            separator = "/"
        else:
            raise ValueError("No separators in $SPLUNK_HOME. Can't determine what file separator to use.")
        appPath = separator.join([splunkHome, "etc", "apps", appName] + pathComponents)
        return appPath

    def uncheckedRestartSplunk(self, timeout=120):
        self.service.restart(timeout)

    def restartSplunk(self, timeout=120):
        if self.service.restart_required:
            self.service.restart(timeout)
        else:
            raise NoRestartRequiredError()

    @classmethod
    def setUpClass(cls):
        cls.opts = parse([], {}, ".splunkrc")

        # Before we start, make sure splunk doesn't need a restart.
        service = client.connect(**cls.opts.kwargs)
        if service.restart_required:
            service.restart(timeout=120)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.service = client.connect(**self.opts.kwargs)
        # If Splunk is in a state requiring restart, go ahead
        # and restart. That way we'll be sane for the rest of
        # the test.
        if self.service.restart_required:
            self.restartSplunk()
        logging.debug("Connected to splunkd version %s", '.'.join(str(x) for x in self.service.splunk_version))

    def tearDown(self):
        from splunklib.binding import HTTPError

        if self.service.restart_required:
            self.fail("Test left Splunk in a state requiring a restart.")

        for appName in self.installedApps:
            if appName in self.service.apps:
                try:
                    self.service.apps.delete(appName)
                    wait(lambda: appName not in self.service.apps)
                except HTTPError as error:
                    if not (os.name == 'nt' and error.status == 500):
                        raise
                    print 'Ignoring failure to delete {0} during tear down: {1}'.format(appName, error)
        if self.service.restart_required:
            self.clear_restart_message()