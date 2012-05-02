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

import re
import sys
from time import sleep
import unittest

# Run the test suite on the SDK without installing it.
sys.path.insert(0, '../') 
sys.path.insert(0, '../examples')

from utils import parse

def delete_app(service, name):
    """Delete the app with the given name at the given service."""
    apps = service.apps
    if name in apps:
        app = apps[name]
        app.disable()
        apps.delete(name)
        restart(service)

def restart(service, timeout=120):
    """Restart the given service and wait for it to wake back up."""
    service.restart()
    sleep(5) # Wait for service to notice restart
    secs = 0
    while secs < timeout:
        try:
            service.login() # Awake yet?
            return
        except:
            sleep(2)
            secs -= 2 # Approximately
    raise Exception, "Operation timed out."

def wait(entity, predicate, timeout=60):
    """Wait for the given entity to satisfy the given condition."""
    secs = 0
    while not predicate(entity):
        if secs > timeout:
            raise Exception, "Operation timed out."
        sleep(1)
        secs += 1
        entity.refresh()
    return entity

class TestCase(unittest.TestCase):
    def check_content(self, entity, **kwargs):
        for k, v in kwargs.iteritems(): 
            self.assertEqual(entity[k], str(v))

    def check_entity(self, entity):
        self.assertTrue(entity.name is not None)
        self.assertTrue(entity.path is not None)

        self.assertTrue(entity.state is not None)
        self.assertTrue(entity.content is not None)

        # Verify access metadata

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

    def setUp(self):
        self.opts = parse([], {}, ".splunkrc")

def main():
    unittest.main()
