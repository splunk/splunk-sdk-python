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

from StringIO import StringIO
import testlib
from time import sleep
import splunklib.results as results
import io


class ResultsTestCase(testlib.SDKTestCase):
    def test_read_from_empty_result_set(self):
        job = self.service.jobs.create("search index=_internal_does_not_exist | head 2")
        while not job.is_done():
            sleep(0.5)
        self.assertEquals(0, len(list(results.ResultsReader(io.BufferedReader(job.results())))))

    def test_read_normal_results(self):
        xml_text = """
<?xml version='1.0' encoding='UTF-8'?>
<results preview='0'>
<meta>
<fieldOrder>
<field>series</field>
<field>sum(kb)</field>
</fieldOrder>
</meta>
<messages>
  <msg type='DEBUG'>base lispy: [ AND ]</msg>
  <msg type='DEBUG'>search context: user='admin', app='search', bs-pathname='/some/path'</msg>
</messages>
	<result offset='0'>
		<field k='series'>
			<value><text>twitter</text></value>
		</field>
		<field k='sum(kb)'>
			<value><text>14372242.758775</text></value>
		</field>
	</result>
	<result offset='1'>
		<field k='series'>
			<value><text>splunkd</text></value>
		</field>
		<field k='sum(kb)'>
			<value><text>267802.333926</text></value>
		</field>
	</result>
	<result offset='2'>
		<field k='series'>
			<value><text>flurry</text></value>
		</field>
		<field k='sum(kb)'>
			<value><text>12576.454102</text></value>
		</field>
	</result>
	<result offset='3'>
		<field k='series'>
			<value><text>splunkd_access</text></value>
		</field>
		<field k='sum(kb)'>
			<value><text>5979.036338</text></value>
		</field>
	</result>
	<result offset='4'>
		<field k='series'>
			<value><text>splunk_web_access</text></value>
		</field>
		<field k='sum(kb)'>
			<value><text>5838.935649</text></value>
		</field>
	</result>
</results>
""".strip()
        expected_results = [
            results.Message('DEBUG', 'base lispy: [ AND ]'),
            results.Message('DEBUG', "search context: user='admin', app='search', bs-pathname='/some/path'"),
            {
                'series': 'twitter',
                'sum(kb)': '14372242.758775',
            },
            {
                'series': 'splunkd',
                'sum(kb)': '267802.333926',
            },
            {
                'series': 'flurry',
                'sum(kb)': '12576.454102',
            },
            {
                'series': 'splunkd_access',
                'sum(kb)': '5979.036338',
            },
            {
                'series': 'splunk_web_access',
                'sum(kb)': '5838.935649',
            },
        ]

        self.assert_parsed_results_equals(xml_text, expected_results)

    def test_read_raw_field(self):
        xml_text = """
<?xml version='1.0' encoding='UTF-8'?>
<results preview='0'>
<meta>
<fieldOrder>
<field>_raw</field>
</fieldOrder>
</meta>
	<result offset='0'>
		<field k='_raw'><v xml:space='preserve' trunc='0'>07-13-2012 09:27:27.307 -0700 INFO  Metrics - group=search_concurrency, system total, active_hist_searches=0, active_realtime_searches=0</v></field>
	</result>
</results>
""".strip()
        expected_results = [
            {
                '_raw': '07-13-2012 09:27:27.307 -0700 INFO  Metrics - group=search_concurrency, system total, active_hist_searches=0, active_realtime_searches=0',
            },
        ]

        self.assert_parsed_results_equals(xml_text, expected_results)

    def test_read_raw_field_with_segmentation(self):
        xml_text = """
<?xml version='1.0' encoding='UTF-8'?>
<results preview='0'>
<meta>
<fieldOrder>
<field>_raw</field>
</fieldOrder>
</meta>
	<result offset='0'>
		<field k='_raw'><v xml:space='preserve' trunc='0'>07-13-2012 09:27:27.307 -0700 INFO  Metrics - group=search_concurrency, <sg h="1">system total</sg>, <sg h="2">active_hist_searches=0</sg>, active_realtime_searches=0</v></field>
	</result>
</results>
""".strip()
        expected_results = [
            {
                '_raw': '07-13-2012 09:27:27.307 -0700 INFO  Metrics - group=search_concurrency, system total, active_hist_searches=0, active_realtime_searches=0',
            },
        ]

        self.assert_parsed_results_equals(xml_text, expected_results)

    def assert_parsed_results_equals(self, xml_text, expected_results):
        results_reader = results.ResultsReader(StringIO(xml_text))
        actual_results = [x for x in results_reader]
        self.assertEquals(expected_results, actual_results)

if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()