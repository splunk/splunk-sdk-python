#!/usr/bin/env python
#
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

"""Shared unit test utilities."""

import sys
# Run the test suite on the SDK without installing it.
sys.path.insert(0, '../')
sys.path.insert(0, '../examples')

import re
import warnings
import splunklib.data as data
import splunklib.client as client
from time import sleep
from datetime import datetime, timedelta
import unittest
from utils import parse
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

    def assertEventuallyEqual(self, expected, func, timeout=10, pause_time=0.5,
                              timeout_message="Operation timed out."):
        self.assertEventuallyTrue(
            lambda: expected == func(),
            timeout=timeout, pause_time=pause_time,
            timeout_message=timeout_message
        )

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

    def clearRestartMessage(self):
        try:
            self.service.delete("messages/restart_required")
        except client.HTTPError as he:
            if he.status == 404:
                pass
            else:
                raise

    def installAppFromCollection(self, name):
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
        self.installedApps.append(name)

    def pathInApp(self, appName, pathComponents):
        """Return a path to *pathComponents* in *appName*.

        *pathComponents* shold be a list of strings giving the components.
        This function will try to figure out the correct separator (/ or \)
        for the platform that splunkd is running on and construct the path
        as needed.

        :return: A string giving the path.
        """
        splunkHome = self.service.settings['SPLUNK_HOME']
        if "/" in splunkHome and "\\" in splunkHome:
            raise ValueError("There are both forward and back slashes in $SPLUNK_HOME. What system are you on?!?")
        elif "/" in splunkHome:
            separator = "/"
        elif "\\" in splunkHome:
            separator = "\\"
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
        if self.service.restart_required:
            self.restartSplunk()
        logging.debug("Connected to splunkd version %s", '.'.join(str(x) for x in self.service.splunk_version))

    def tearDown(self):
        if self.service.restart_required:
            self.fail("Test left Splunk in a state requiring a restart.")
        for appName in self.installedApps:
            if appName in self.service.apps:
                self.service.apps.delete(appName)
                wait(lambda: appName not in self.service.apps)
        if self.service.restart_required:
            self.clearRestartMessage()