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
import splunklib.client as client
try:
    import unittest
except ImportError:
    import unittest2 as unittest


class IndexTest(testlib.SDKTestCase):
    def setUp(self):
        super(IndexTest, self).setUp()
        self.index_name = testlib.tmpname()
        self.index = self.service.indexes.create(self.index_name)
        self.assertEventuallyTrue(lambda: self.index.refresh()['disabled'] == '0')

    def tearDown(self):
        super(IndexTest, self).tearDown()
        # We can't delete an index with the REST API before Splunk
        # 5.0. In 4.x, we just have to leave them lying around until
        # someone cares to go clean them up. Unique naming prevents
        # clashes, though.
        if self.service.splunk_version >= (5,):
            if self.index_name in self.service.indexes:
                self.service.indexes.delete(self.index_name)
            self.assertEventuallyTrue(lambda: self.index_name not in self.service.indexes)
        else:
            logging.warning("test_index.py:TestDeleteIndex: Skipped: cannot "
                            "delete indexes via the REST API in Splunk 4.x")

    def totalEventCount(self):
        self.index.refresh()
        return int(self.index['totalEventCount'])

    def test_delete(self):
        if self.service.splunk_version >= (5,):
            self.assertTrue(self.index_name in self.service.indexes)
            self.service.indexes.delete(self.index_name)
            self.assertEventuallyTrue(lambda: self.index_name not in self.service.indexes)

    def test_integrity(self):
        self.check_entity(self.index)

    def test_default(self):
        default = self.service.indexes.get_default()
        self.assertTrue(isinstance(default, str))

    def test_disable_enable(self):
        self.index.disable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '1')
        self.index.enable()
        self.index.refresh()
        self.assertEqual(self.index['disabled'], '0')

    def test_submit_and_clean(self):
        self.index.refresh()
        original_count = int(self.index['totalEventCount'])
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        self.assertEventuallyTrue(lambda: self.totalEventCount() == original_count+1, timeout=50)

        # Cleaning an enabled index on 4.x takes forever, so we disable it.
        # However, cleaning it on 5 requires it to be enabled.
        if self.service.splunk_version < (5,):
            self.index.disable()
            self.restartSplunk()
        self.index.clean(timeout=500)
        self.assertEqual(self.index['totalEventCount'], '0')

    def test_prefresh(self):
        self.assertEqual(self.index['disabled'], '0') # Index is prefreshed

    def test_submit(self):
        event_count = int(self.index['totalEventCount'])
        self.assertEqual(self.index['sync'], '0')
        self.assertEqual(self.index['disabled'], '0')
        self.index.submit("Hello again!", sourcetype="Boris", host="meep")
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+1, timeout=50)

    def test_submit_via_attach(self):
        event_count = int(self.index['totalEventCount'])
        cn = self.index.attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+1, timeout=60)

    def test_submit_via_attached_socket(self):
        event_count = int(self.index['totalEventCount'])
        f = self.index.attached_socket
        with f() as sock:
            sock.send('Hello world!\r\n')
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+1, timeout=60)

    def test_submit_via_attach_with_cookie_header(self):
        # Skip this test if running below Splunk 6.2, cookie-auth didn't exist before
        splver = self.service.splunk_version
        if splver[:2] < (6, 2):
            self.skipTest("Skipping cookie-auth tests, running in %d.%d.%d, this feature was added in 6.2+" % splver)

        event_count = int(self.service.indexes[self.index_name]['totalEventCount'])

        cookie = "%s=%s" % (self.service.http._cookies.items()[0])
        service = client.Service(**{"cookie": cookie})
        service.login()
        cn = service.indexes[self.index_name].attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+1, timeout=60)

    def test_submit_via_attach_with_multiple_cookie_headers(self):
        # Skip this test if running below Splunk 6.2, cookie-auth didn't exist before
        splver = self.service.splunk_version
        if splver[:2] < (6, 2):
            self.skipTest("Skipping cookie-auth tests, running in %d.%d.%d, this feature was added in 6.2+" % splver)

        event_count = int(self.service.indexes[self.index_name]['totalEventCount'])
        service = client.Service(**{"cookie": 'a bad cookie'})
        service.http._cookies.update(self.service.http._cookies)
        service.login()
        cn = service.indexes[self.index_name].attach()
        cn.send("Hello Boris!\r\n")
        cn.close()
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+1, timeout=60)

    def test_upload(self):
        if not self.app_collection_installed():
            print "Test requires sdk-app-collection. Skipping."
            return
        self.install_app_from_collection("file_to_upload")

        event_count = int(self.index['totalEventCount'])

        path = self.pathInApp("file_to_upload", ["log.txt"])
        self.index.upload(path)
        self.assertEventuallyTrue(lambda: self.totalEventCount() == event_count+4, timeout=60)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
