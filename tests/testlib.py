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
from time import sleep
import unittest

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
    def setUp(self):
        self.opts = parse([], {}, ".splunkrc")

def main():
    unittest.main()
