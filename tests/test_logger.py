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

import splunklib.client as client

import testlib

LEVELS = ["INFO", "WARN", "ERROR", "DEBUG", "CRIT"]

class TestCase(testlib.TestCase):
    def test_read(self):
        service = client.connect(**self.opts.kwargs)
        
        for logger in service.loggers:
            logger.name
            logger.path
            logger.content
            self.assertTrue(logger['level'] in LEVELS)

    def test_crud(self):
        service = client.connect(**self.opts.kwargs)

        self.assertTrue(service.loggers.contains("AuditLogger"))
        logger = service.loggers['AuditLogger']

        saved = logger['level']
        for level in LEVELS:
            logger.update(level=level)
            logger.refresh()
            self.assertEqual(service.loggers['AuditLogger']['level'], level)

        logger.update(level=saved)
        logger.refresh()
        self.assertEqual(service.loggers['AuditLogger']['level'], saved)

if __name__ == "__main__":
    testlib.main()
