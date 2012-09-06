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
import unittest
import os
from cStringIO import StringIO
import tempfile
import splunklib.export as export

events = [{'_time':10}, {'_time':70}, {'_time':125}, {'_time':135}, {'_time':3601}, {'_time':3671}]

def search_func(index_name, earliest_time, latest_time, offset=0):
    return [e for e in events if e['_time'] >= earliest_time and e['_time'] < latest_time][offset:]

def timeline_func(index_name, earliest_time, latest_time, span):
    """Mock function for getting an event timeline.

    Returns an ordered list of dicts with the keys

        * 'earliest_time' (number giving time in seconds since the epoch)
        * 'n_events' (non-negative integer giving the number of events in this bucket)
        * 'span' (a number giving the duration of this bucket in seconds)
    """
    buckets = []
    time = earliest_time
    while time < latest_time:
        bucket = {'earliest_time': time,
                  'n_events': len([x for x in events if x['_time'] < time+span and x['_time'] >= time]),
                  'span': span}
        buckets.append(bucket)
        time += span
    buckets[-1]['span'] = latest_time - buckets[-1]['earliest_time']
    return buckets

class TestBucketBehavior(unittest.TestCase):
    maxDiff = None

    def test_refine_case1(self):
        b = export.FreshBucket(
            index_name='abc',
            earliest_time=0,
            latest_time=3700,
        )
        buckets = b.refine(timeline_func, 1, 2)
        expected = [export.FreshBucket('abc', 60*i, 60*(i+1))
                    for i in range(0, 60)] +\
                   [export.FreshBucket('abc', 3600, 3700)]
        self.assertEqual(expected, buckets)

    def test_refine_case2(self):
        b = export.FreshBucket(
            index_name='abc',
            earliest_time=0,
            latest_time=200,
        )
        buckets = b.refine(timeline_func, 1, 2)
        expected = [export.FreshBucket('abc', 0, 60),
                    export.FreshBucket('abc', 60, 120),
                    export.FreshBucket('abc', 120, 180),
                    export.FreshBucket('abc', 180, 200)]
        self.assertEqual(expected, buckets)

    def test_refine_case3(self):
        b = export.FreshBucket(
            index_name='abc',
            earliest_time=0,
            latest_time=86400,
        )
        buckets = b.refine(timeline_func, min_span=1, event_limit=50)
        self.assertEqual(buckets, [b])

    def test_refine_case4(self):
        b = export.FreshBucket(
            index_name='abc',
            earliest_time=0,
            latest_time=86400,
        )
        buckets = b.refine(timeline_func, min_span=86400, event_limit=2)
        self.assertEqual([b], buckets)

    def test_invalid_fresh_constructor(self):
        self.assertRaises(
            ValueError,
            export.FreshBucket,
            index_name='abc',
            earliest_time=0,
            latest_time=0,
        )

    def test_invalid_partial_constructor(self):
        self.assertRaises(
            ValueError,
            export.PartialBucket,
            index_name='abc',
            earliest_time=0,
            latest_time=0,
            offset=0
        )

    def test_invalid_finished_constructor(self):
        self.assertRaises(
            ValueError,
            export.FinishedBucket,
            index_name='abc',
            earliest_time=0,
            latest_time=0,
            n_events=12
        )

    def test_iter_finished_bucket(self):
        bucket = export.FinishedBucket(
            index_name='index',
            earliest_time=0,
            latest_time=10,
            n_events=12
        )
        self.assertRaises(StopIteration, bucket.events(search_func).next)

    def test_iter_fresh_bucket(self):
        bucket = export.FreshBucket(
            index_name='index',
            earliest_time=0,
            latest_time=10000,
        )
        found = list(bucket.events(search_func))
        self.assertEqual(events, found)

    def test_iter_partial_bucket(self):
        N = 4
        bucket = export.PartialBucket(
            index_name='index',
            earliest_time=0,
            latest_time=100000,
            offset=N
        )
        self.assertEqual(events[N:], list(bucket.events(search_func)))

    def test_equals(self):
        self.assertEqual(
            export.FreshBucket('abc', 0, 10),
            export.FreshBucket('abc', 0, 10)
        )
        self.assertNotEqual(
            export.FreshBucket('abc', 0, 10),
            export.FreshBucket('def', 0, 10)
        )
        self.assertNotEqual(
            export.FreshBucket('abc', 0, 10),
            export.PartialBucket('abc', 0, 10, 0)
        )
        self.assertEqual(
            export.PartialBucket('abc', 0, 10, 0),
            export.PartialBucket('abc', 0, 10, 0)
        )
        self.assertNotEqual(
            export.PartialBucket('abc', 0, 10, 0),
            export.PartialBucket('abc', 0, 10, 5)
        )
        self.assertNotEqual(
            export.PartialBucket('abc', 0, 10, 0),
            export.FinishedBucket('abc', 0, 10, 12)
        )
        self.assertEqual(
            export.FinishedBucket('abc', 0, 10, 12),
            export.FinishedBucket('abc', 0, 10, 12)
        )


    def test_timeline_func(self):
        self.assertEqual(
            timeline_func('abc', 0, 100, 60),
            [{'earliest_time': 0, 'n_events': 1, 'span': 60},
             {'earliest_time': 60, 'n_events': 1, 'span': 40}]
        )

    def test_restart_path(self):
        path = export.default_restart_path('abc', 52, 550)
        self.assertTrue(path.startswith('/'))
        self.assertEqual('abc-52-550.rst', path.split('/')[-1])

    def test_read_null_terminated_ascii_string(self):
        h = StringIO('this is a test\0')
        self.assertEqual(
            'this is a test',
            export.read_null_terminated_ascii_string(h)
        )

        h = StringIO('this is a test\0and more text')
        self.assertEqual(
            'this is a test',
            export.read_null_terminated_ascii_string(h)
        )

        h = StringIO('this should raise an error')
        self.assertRaises(
            ValueError,
            export.read_null_terminated_ascii_string,
            h
        )

        h = StringIO('this is a test'*500)
        self.assertRaises(
            ValueError,
            export.read_null_terminated_ascii_string,
            h
        )

    def test_read_write_null_terminated_ascii_string(self):
        expected = 'this is a test'
        h = StringIO()
        intermediate = export.write_null_terminated_ascii_string(h, expected)
        h.seek(0)
        found = export.read_null_terminated_ascii_string(h)
        self.assertEqual(expected, found)

    def test_read_int64(self):
        h = StringIO('abcdefgh')
        # Check this value in your favorite hex editor
        expected = 0x6162636465666768
        self.assertEqual(expected, export.read_int64(h))

    def test_write_int64(self):
        val = 0x6162636465666768
        h = StringIO()
        export.write_int64(h, val)
        h.seek(0)
        self.assertEqual('abcdefgh', h.read())

    def test_read_plan(self):
        with open('clean_restart_plan.rst', 'rb') as h:
            found_plan = export.read_plan(h)
        expected_plan = [export.FreshBucket(index_name='this index name',
                                            earliest_time=a,
                                            latest_time=b)
                         for (a,b) in [(0x1414123123123124, 0x1524234242342342),
                                       (0x2304411141414235, 0x2342352563424235),
                                       (0x3424234234234234, 0x5225522211234234)]]
        self.assertEqual(expected_plan, found_plan)

    def test_write_plan(self):
        plan = [export.FreshBucket(
                    index_name='this index name',
                    earliest_time=a,
                    latest_time=b
                ) for (a,b) in [(0x1414123123123124, 0x1524234242342342),
                                (0x2304411141414235, 0x2342352563424235),
                                (0x3424234234234234, 0x5225522211234234)]]
        with open('clean_restart_plan.rst', 'rb') as h:
            expected = h.read()
        h = StringIO()
        export.write_plan(h, plan)
        h.seek(0)
        self.assertEqual(expected, h.read())

    def test_read_log(self):
        with open('restart_plan_with_log.rst', 'rb') as h:
            export.read_plan(h)
            log = export.read_log(h)
        expected_log = [{'bucket': 0, 'offset': 5},
                        {'bucket': 1, 'offset': 3},
                        {'bucket': 2, 'offset': 4}]
        self.assertEqual(expected_log, log)

    def test_writing_log_entries(self):
        h = tempfile.TemporaryFile(mode='r+b')
        self.assertEqual(h.mode, 'r+b')
        export.write_log_entry(h, 65, 12)
        expected = '\0\0\0\0\0\0\0A\0\0\0\0\0\0\0\x0C'
        h.seek(0)
        self.assertEqual(expected, h.read())

        expected = '\0\0\0\0\0\0\0A\0\0\0\0\0\0\0\x0A'
        export.update_log_entry(h, 10)
        h.seek(0)
        self.assertEqual(expected, h.read())

    def test_update_plans(self):
        plan = [export.FreshBucket('abc', 0, 60),
                export.FreshBucket('abc', 60, 120),
                export.FreshBucket('abc', 120, 180),
                export.FreshBucket('abc', 180, 200)]
        log = [{'bucket': 0, 'offset': 5},
               {'bucket': 1, 'offset': 3},
               {'bucket': 2, 'offset': 4}]
        new_plan = export.update_plan_with_log(plan, log)
        expected = [export.FinishedBucket('abc', 0, 60, 5),
                    export.FinishedBucket('abc', 60, 120, 3),
                    export.PartialBucket('abc', 120, 180, offset=4),
                    export.FreshBucket('abc', 180, 200)]
        self.assertEqual(expected, new_plan)

    def test_rewind_plan(self):
        plan = [export.FinishedBucket('abc', 0, 60, 5),
                export.FinishedBucket('abc', 60, 120, 3),
                export.PartialBucket('abc', 120, 180, offset=4),
                export.FreshBucket('abc', 180, 200)]
        cases = {0: plan,
                 1: [export.FinishedBucket('abc', 0, 60, 5),
                     export.FinishedBucket('abc', 60, 120, 3),
                     export.PartialBucket('abc', 120, 180, offset=3),
                     export.FreshBucket('abc', 180, 200)],
                 4: [export.FinishedBucket('abc', 0, 60, 5),
                     export.FinishedBucket('abc', 60, 120, 3),
                     export.FreshBucket('abc', 120, 180),
                     export.FreshBucket('abc', 180, 200)],
                 6: [export.FinishedBucket('abc', 0, 60, 5),
                     export.PartialBucket('abc', 60, 120, 1),
                     export.FreshBucket('abc', 120, 180),
                     export.FreshBucket('abc', 180, 200)],
                 10: [export.PartialBucket('abc', 0, 60, 2),
                      export.FreshBucket('abc', 60, 120),
                      export.FreshBucket('abc', 120, 180),
                       export.FreshBucket('abc', 180, 200)]
                 }
        for n, expected in cases.iteritems():
            n, new_plan = export.rewind_plan(plan, n)
            self.assertEqual(expected, new_plan)

    def test_restart_file(self):
        plan = [export.FreshBucket('this index name', 0, 60),
                export.FreshBucket('this index name', 60, 120),
                export.FreshBucket('this index name', 120, 180),
                export.FreshBucket('this index name', 180, 200)]
        rf = export.RestartFile('test.rst', plan=plan, overwrite=True)
        for i in range(5):
            rf.log(0, i+1)
        for i in range(3):
            rf.log(1, i+1)
        for i in range(4):
            rf.log(2, i+1)
        rf.close()

        rf = export.RestartFile('test.rst')
        expected_plan = [export.FinishedBucket('this index name', 0, 60, 5),
                         export.FinishedBucket('this index name', 60, 120, 3),
                         export.PartialBucket('this index name', 120, 180, offset=4),
                         export.FreshBucket('this index name', 180, 200)]
        self.assertEqual(expected_plan, rf.plan)

    def test_index_exporter_with_rewind(self):
        plan = [export.FreshBucket('this index name', 0, 60),
                export.FreshBucket('this index name', 60, 120),
                export.FreshBucket('this index name', 120, 180),
                export.FreshBucket('this index name', 180, 10000)]
        rf = export.RestartFile('test.rst', plan=plan, overwrite=True)
        rf.close()

        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
            rewind=3
        )
        self.assertEqual(ie.n_rewound, 0)
        self.assertEqual(events, list(ie))

    def test_index_exporter_with_forward_and_rewind(self):
        plan = [export.FreshBucket('this index name', 0, 60),
                export.FreshBucket('this index name', 60, 120),
                export.FreshBucket('this index name', 120, 180),
                export.FreshBucket('this index name', 180, 10000)]
        rf = export.RestartFile('test.rst', plan=plan, overwrite=True)
        rf.log(0, 1)
        rf.log(1, 1)
        rf.close()

        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
            rewind=3
        )
        self.assertEqual(ie.n_rewound, 2)
        self.assertEqual(events, list(ie))

    def test_index_exporter_with_forward(self):
        plan = [export.FreshBucket('this index name', 0, 60),
                export.FreshBucket('this index name', 60, 120),
                export.FreshBucket('this index name', 120, 180),
                export.FreshBucket('this index name', 180, 10000)]
        rf = export.RestartFile('test.rst', plan=plan, overwrite=True)
        rf.log(0, 1)
        rf.log(1, 1)
        rf.close()

        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
        )
        self.assertEqual(ie.n_rewound, 0)
        self.assertEqual(events[2:], list(ie))

    def test_index_exporter_with_restart(self):
        if os.path.exists('test.rst'):
            os.unlink('test.rst')
        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
        )
        for i in range(2):
            self.assertEqual(events[i], ie.next())

        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
        )
        for i in range(2, 6):
            self.assertEqual(events[i], ie.next())

    def test_index_exporter_with_restart_and_rewind(self):
        if os.path.exists('test.rst'):
            os.unlink('test.rst')
        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
        )
        for i in range(2):
            self.assertEqual(events[i], ie.next())

        ie = export.IndexExporter(
            index_name='this index name',
            earliest_time=0,
            latest_time=10000,
            search_func=search_func,
            timeline_func=timeline_func,
            restart='test.rst',
            rewind = 1
        )
        for i in range(1, 6):
            self.assertEqual(events[i], ie.next())


if __name__ == "__main__":
    testlib.main()
