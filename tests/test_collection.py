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

expected_access_keys = set(['sharing', 'app', 'owner'])
expected_fields_keys = set(['required', 'optional', 'wildcard'])


class CollectionTestCase(testlib.SDKTestCase):
    def setUp(self):
        super(CollectionTestCase, self).setUp()
        if self.service.splunk_version[0] >= 5 and 'modular_input_kinds' not in collections:
            collections.append('modular_input_kinds') # Not supported before Splunk 5.0
        else:
            logging.info("Skipping modular_input_kinds; not supported by Splunk %s" % \
                         '.'.join(str(x) for x in self.service.splunk_version))
        for saved_search in self.service.saved_searches:
            if saved_search.name.startswith('delete-me'):
                try:
                    for job in saved_search.history():
                        job.cancel()
                    self.service.saved_searches.delete(saved_search.name)
                except KeyError:
                    pass

    def test_metadata(self):
        self.assertRaises(client.NotSupportedError, self.service.jobs.itemmeta)
        self.assertRaises(client.NotSupportedError, self.service.loggers.itemmeta)
        self.assertRaises(TypeError, self.service.inputs.itemmeta)
        for c in collections:
            if c in ['jobs', 'loggers', 'inputs', 'modular_input_kinds']:
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
            expected = [ent.name for ent in coll.list(count=10, sort_mode="auto")]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list()][:10]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_count(self):
        N = 5
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(count=N+5)][:N]
            N = len(expected) # in case there are <N elements
            found = [ent.name for ent in coll.list(count=N)]
            self.assertEqual(expected, found,
                             msg='on %s (expected %s, found %s' % \
                                 (coll_name, expected, found))

    def test_list_with_offset(self):
        import random
        for offset in [random.randint(3,50) for x in range(5)]:
            for coll_name in collections:
                coll = getattr(self.service, coll_name)
                expected = [ent.name for ent in coll.list(count=offset+10)][offset:]
                found = [ent.name for ent in coll.list(offset=offset, count=10)]
                self.assertEqual(expected, found,
                                 msg='on %s (expected %s, found %s)' % \
                                     (coll_name, expected, found))

    def test_list_with_search(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list()]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            # TODO: DVPL-5868 - This should use a real search instead of *. Otherwise the test passes trivially.
            found = [ent.name for ent in coll.list(search="*")]
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_sort_dir(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected_kwargs = {'sort_dir': 'desc'}
            found_kwargs = {'sort_dir': 'asc'}
            if coll_name == 'jobs':
                expected_kwargs['sort_key'] = 'sid'
                found_kwargs['sort_key'] = 'sid'
            expected = list(reversed([ent.name for ent in coll.list(**expected_kwargs)]))
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            found = [ent.name for ent in coll.list(**found_kwargs)]

            self.assertEqual(sorted(expected), sorted(found),
                             msg='on %s (expected: %s, found: %s)' %
                                 (coll_name, expected, found))

    def test_list_with_sort_mode_auto(self):
        # The jobs collection requires special handling. The sort_dir kwarg is
        # needed because the default sorting direction for jobs is "desc", not
        # "asc". The sort_key kwarg is required because there is no default
        # sort_key for jobs in Splunk 6.
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            if coll_name == 'jobs':
                expected = [ent.name for ent in coll.list(
                    sort_mode="auto", sort_dir="asc", sort_key="sid")]
            else:
                expected = [ent.name for ent in coll.list(sort_mode="auto")]

            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)

            if coll_name == 'jobs':
                found = [ent.name for ent in coll.list(
                    sort_dir="asc", sort_key="sid")]
            else:
                found = [ent.name for ent in coll.list()]

            self.assertEqual(expected, found, msg='on %s (expected: %s, found: %s)' % (coll_name, expected, found))

    def test_list_with_sort_mode_alpha_case(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            # sort_dir is needed because the default sorting direction
            # for jobs is "desc", not "asc", so we have to set it explicitly or our tests break.
            kwargs = {'sort_mode': 'alpha_case', 'sort_dir': 'asc', 'count': 30}
            if coll_name == 'jobs':
                kwargs['sort_key'] = 'sid'
            found = [ent.name for ent in coll.list(**kwargs)]
            if len(found) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            expected = sorted(found)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))

    def test_list_with_sort_mode_alpha(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            # sort_dir is needed because the default sorting direction
            # for jobs is "desc", not "asc", so we have to set it explicitly
            # or our tests break. We also need to specify "sid" as sort_key
            # for jobs, or things are sorted by submission time and ties go
            # the same way in either sort direction.
            kwargs = {'sort_mode': 'alpha', 'sort_dir': 'asc', 'count': 30}
            if coll_name == 'jobs':
                kwargs['sort_key'] = 'sid'
            found = [ent.name for ent in coll.list(**kwargs)]
            if len(found) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            expected = sorted(found, key=str.lower)
            self.assertEqual(expected, found,
                             msg='on %s (expected: %s, found: %s)' % \
                                 (coll_name, expected, found))
        
    def test_iteration(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            expected = [ent.name for ent in coll.list(count=10)]
            if len(expected) == 0:
                logging.debug("No entities in collection %s; skipping test.", coll_name)
            total = len(expected)
            found = []
            for ent in coll.iter(pagesize=max(int(total/5.0), 1), count=10):
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

    def test_getitem_with_nonsense(self):
        for coll_name in collections:
            coll = getattr(self.service, coll_name)
            name = testlib.tmpname()
            self.assertTrue(name not in coll)
            self.assertRaises(KeyError, coll.__getitem__, name)
    
    def test_getitem_with_namespace_sample_in_changelog(self):
        from splunklib.binding import namespace
        ns = client.namespace(owner='nobody', app='search')
        result = self.service.saved_searches['Top five sourcetypes', ns]

    def test_collection_search_get(self):
        for search in self.service.saved_searches:
            self.assertEqual(self.service.saved_searches[search.name].path, search.path)
            self.assertEqual(200, self.service.saved_searches.get(search.name).status)

    def test_collection_inputs_getitem(self):
        valid_kinds = self.service.inputs._get_kind_list()
        valid_kinds.remove("script")
        for inp in self.service.inputs.list(*valid_kinds):
            self.assertTrue(self.service.inputs[inp.name])



if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()

