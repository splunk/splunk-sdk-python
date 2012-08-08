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

import testlib
import logging

from contextlib import contextmanager

import splunklib.client as client

collections = [
    'apps',
    'event_types',
    'indexes',
    'inputs',
    'jobs',
    'loggers',
    'messages',
    'roles',
    'users'
    ]

expected_access_keys = set(['sharing', 'app', 'owner',])
expected_fields_keys = set(['required', 'optional', 'wildcard'])


class TestCase(testlib.TestCase):
    def test_metadata(self):
        self.assertRaises(client.NotSupportedError, self.service.jobs.itemmeta)
        self.assertRaises(client.NotSupportedError, self.service.loggers.itemmeta)
        self.assertRaises(TypeError, self.service.inputs.itemmeta)
        for c in collections:
            if c in ['jobs', 'loggers', 'inputs']:
                continue
            coll = getattr(self.service, c)
            metadata = coll.itemmeta()
            found_access_keys = set(metadata.access.keys())
            found_fields_keys = set(metadata.fields.keys())
            self.assertTrue(found_access_keys >= expected_access_keys,
                            msg='metadata.access is missing keys on ' + \
                                '%s (found: %s, expected: %s)' % \
                                (coll, found_access_keys, 
                                 expected_access_keys))
            self.assertTrue(found_fields_keys >= expected_fields_keys,
                            msg='metadata.fields is missing keys on ' + \
                                '%s (found: %s, expected: %s)' % \
                                (coll, found_fields_keys, 
                                 expected_fields_keys))

    def test_list(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(sort_mode="auto")]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list()]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_search(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list()]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list(search="*")]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))
            return expected, found

    def test_list_with_sort_dir(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = list(reversed([ent.name for ent in coll.list(sort_dir="desc")]))
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list(sort_dir="asc")]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_sort_mode_auto(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(sort_mode="auto")]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list()]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_sort_mode_alpha_case(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            found = [ent.name for ent in coll.list(sort_mode="alpha_case", count=30)]
            if len(found) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            expected = sorted(found)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_sort_mode_alpha(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            found = [ent.name for ent in coll.list(sort_mode="alpha", count=30)]
            if len(found) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            expected = sorted(found, key=str.lower)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))
        
    def test_iteration(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(count=30)]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            total = len(expected)
            found = []
            for ent in coll.iter(pagesize=max(int(total/5.0), 1), count=30):
                found.append(ent.name)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_paging(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(count=30)]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            total = len(expected)
            page_size = max(int(total/5.0), 1)
            found = []
            offset = 0
            while offset < total:
                page = coll.list(offset=offset, count=page_size)
                count = len(page)
                offset += count
                self.assertTrue(count == page_size or offset == total,
                                msg='on %s' % coll_name)
                found.extend([ent.name for ent in page])
                logging.debug("Iterate: offset=%d/%d", offset, total)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

if __name__ == "__main__":
    testlib.main()

