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

import testlib

import splunklib.client as client

LEVELS = ["INFO", "WARN", "ERROR", "DEBUG", "CRIT"]

class LoggerTestCase(testlib.SDKTestCase):
    def check_logger(self, logger):
        self.check_entity(logger)
        self.assertTrue(logger['level'] in LEVELS)

    def test_read(self):
        for logger in self.service.loggers.list(count=10):
            self.check_logger(logger)

    def test_crud(self):
        self.assertTrue('AuditLogger' in self.service.loggers)
        logger = self.service.loggers['AuditLogger']

        saved = logger['level']
        for level in LEVELS:
            logger.update(level=level)
            logger.refresh()
            self.assertEqual(self.service.loggers['AuditLogger']['level'], level)

        logger.update(level=saved)
        logger.refresh()
        self.assertEqual(self.service.loggers['AuditLogger']['level'], saved)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
