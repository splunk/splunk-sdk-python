#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2015 Splunk, Inc.
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

import gzip
import io
import json
import os
import random
import sys

import pytest
from functools import wraps
from itertools import chain
from sys import float_info
from tempfile import mktemp
from time import time
from types import MethodType
from unittest import main, TestCase

from collections import OrderedDict
from collections import namedtuple, deque

from splunklib.searchcommands.internals import MetadataDecoder, MetadataEncoder, Recorder, RecordWriterV2
from splunklib.searchcommands import SearchMetric
from io import BytesIO
import pickle


# region Functions for producing random apps

# Confirmed: [minint, maxint) covers the full range of values that xrange allows

minint = (-sys.maxsize - 1) // 2
maxint = sys.maxsize // 2

max_length = 1 * 1024

# generate only non-wide Unicode characters, as in Python 2, to prevent surrogate values
MAX_NARROW_UNICODE = 0xD800 - 1


def random_bytes():
    return os.urandom(random.randint(0, max_length))


def random_dict():

    # We do not call random_bytes because the JSONDecoder raises this UnicodeDecodeError when it encounters
    # bytes outside the UTF-8 character set:
    #
    #   'utf8' codec can't decode byte 0x8d in position 2: invalid start byte
    #
    # One might be tempted to select an alternative encoding, but picking one that works for all bytes is a
    # lost cause. The burden is on the customer to ensure that the strings in the dictionaries they serialize
    # contain utf-8 encoded byte strings or--better still--unicode strings. This is because the json package
    # converts all bytes strings to unicode strings before serializing them.

    return OrderedDict((('a', random_float()), ('b', random_unicode()), ('福 酒吧', OrderedDict((('fu', random_float()), ('bar', random_float()))))))


def random_float():
    return random.uniform(float_info.min, float_info.max)


def random_integer():
    return random.uniform(minint, maxint)


def random_integers():
    return random_list(range, minint, maxint)


def random_list(population, *args):
    return random.sample(population(*args), random.randint(0, max_length))


def random_unicode():
    return ''.join([str(x) for x in random.sample(list(range(MAX_NARROW_UNICODE)), random.randint(0, max_length))])

# endregion


@pytest.mark.smoke
class TestInternals(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_object_view(self):

        decoder = MetadataDecoder()
        view = decoder.decode(self._json_input)

        encoder = MetadataEncoder()
        json_output = encoder.encode(view)

        self.assertEqual(self._json_input, json_output)

    def test_record_writer_with_random_data(self, save_recording=False):

        # Confirmed: [minint, maxint) covers the full range of values that xrange allows

        # RecordWriter writes apps in units of maxresultrows records. Default: 50,0000.
        # Partial results are written when the record count reaches maxresultrows.

        writer = RecordWriterV2(BytesIO(), maxresultrows=10)  # small for the purposes of this unit test
        test_data = OrderedDict()

        fieldnames = ['_serial', '_time', 'random_bytes', 'random_dict', 'random_integers', 'random_unicode']
        test_data['fieldnames'] = fieldnames
        test_data['values'] = []

        write_record = writer.write_record

        for serial_number in range(0, 31):
            values = [serial_number, time(), random_bytes(), random_dict(), random_integers(), random_unicode()]
            record = OrderedDict(list(zip(fieldnames, values)))
            #try:
            write_record(record)
            #except Exception as error:
            #    self.fail(error)
            test_data['values'].append(values)

        # RecordWriter accumulates inspector messages and metrics until maxresultrows are written, a partial result
        # is produced or we're finished

        messages = [
            ('debug', random_unicode()),
            ('error', random_unicode()),
            ('fatal', random_unicode()),
            ('info', random_unicode()),
            ('warn', random_unicode())]

        test_data['messages'] = messages

        for message_type, message_text in messages:
            writer.write_message(message_type, '{}', message_text)

        metrics = {
            'metric-1': SearchMetric(1, 2, 3, 4),
            'metric-2': SearchMetric(5, 6, 7, 8)
        }

        test_data['metrics'] = metrics

        for name, metric in list(metrics.items()):
            writer.write_metric(name, metric)

        self.assertEqual(writer._chunk_count, 0)
        self.assertEqual(writer._record_count, 31)
        self.assertEqual(writer.pending_record_count, 31)
        self.assertGreater(writer._buffer.tell(), 0)
        self.assertEqual(writer._total_record_count, 0)
        self.assertEqual(writer.committed_record_count, 0)
        fieldnames.sort()
        writer._fieldnames.sort()
        self.assertListEqual(writer._fieldnames, fieldnames)
        self.assertListEqual(writer._inspector['messages'], messages)

        self.assertDictEqual(
            dict(k_v for k_v in list(writer._inspector.items()) if k_v[0].startswith('metric.')),
            dict(('metric.' + k_v1[0], k_v1[1]) for k_v1 in list(metrics.items())))

        writer.flush(finished=True)

        self.assertEqual(writer._chunk_count, 1)
        self.assertEqual(writer._record_count, 0)
        self.assertEqual(writer.pending_record_count, 0)
        self.assertEqual(writer._buffer.tell(), 0)
        self.assertEqual(writer._buffer.getvalue(), '')
        self.assertEqual(writer._total_record_count, 31)
        self.assertEqual(writer.committed_record_count, 31)

        self.assertRaises(AssertionError, writer.flush, finished=True, partial=True)
        self.assertRaises(AssertionError, writer.flush, finished='non-boolean')
        self.assertRaises(AssertionError, writer.flush, partial='non-boolean')
        self.assertRaises(AssertionError, writer.flush)

        # P2 [ ] TODO: For SCPv2 we should follow the finish negotiation protocol.
        # self.assertRaises(RuntimeError, writer.write_record, {})

        self.assertFalse(writer._ofile.closed)
        self.assertIsNone(writer._fieldnames)
        self.assertDictEqual(writer._inspector, OrderedDict())

        # P2 [ ] TODO: Verify that RecordWriter gives consumers the ability to write partial results by calling
        # RecordWriter.flush(partial=True).

        # P2 [ ] TODO: Verify that RecordWriter gives consumers the ability to finish early by calling
        # RecordWriter.flush(finish=True).

    def _compare_chunks(self, chunks_1, chunks_2):
        self.assertEqual(len(chunks_1), len(chunks_2))
        n = 0
        for chunk_1, chunk_2 in zip(chunks_1, chunks_2):
            self.assertDictEqual(
                chunk_1.metadata, chunk_2.metadata,
                'Chunk {0}: metadata error: "{1}" != "{2}"'.format(n, chunk_1.metadata, chunk_2.metadata))
            self.assertMultiLineEqual(chunk_1.body, chunk_2.body, 'Chunk {0}: data error'.format(n))
            n += 1

    def _load_chunks(self, ifile):
        import re

        pattern = re.compile(r'chunked 1.0,(?P<metadata_length>\d+),(?P<body_length>\d+)\n')
        decoder = json.JSONDecoder()

        chunks = []

        while True:

            line = ifile.readline()

            if len(line) == 0:
                break

            match = pattern.match(line)
            self.assertIsNotNone(match)

            metadata_length = int(match.group('metadata_length'))
            metadata = ifile.read(metadata_length)
            metadata = decoder.decode(metadata)

            body_length = int(match.group('body_length'))
            body = ifile.read(body_length) if body_length > 0 else ''

            chunks.append(TestInternals._Chunk(metadata, body))

        return chunks

    _Chunk = namedtuple('Chunk', ('metadata', 'body'))

    _dictionary = {
        'a': 1,
        'b': 2,
        'c': {
            'd': 3,
            'e': 4,
            'f': {
                'g': 5,
                'h': 6,
                'i': 7
            },
            'j': 8,
            'k': 9
        },
        'l': 10,
        'm': 11,
        'n': 12
    }

    _json_input = str(json.dumps(_dictionary, separators=(',', ':')))
    _package_path = os.path.dirname(os.path.abspath(__file__))


class TestRecorder:

    def __init__(self, test_case):

        self._test_case = test_case
        self._output = None
        self._recording = None
        self._recording_part = None

        def _not_implemented(self):
            raise NotImplementedError('class {} is not in playback or record mode'.format(self.__class__.__name__))

        self.get = self.next_part = self.stop = MethodType(_not_implemented, self, self.__class__)

    @property
    def output(self):
        return self._output

    def playback(self, path):

        with open(path, 'rb') as f:
            test_data = pickle.load(f)

        self._output = BytesIO()
        self._recording = test_data['inputs']
        self._recording_part = self._recording.popleft()

        def get(self, method, *args, **kwargs):
            return self._recording_part[method.__name__].popleft()

        self.get = MethodType(get, self, self.__class__)

        def next_part(self):
            self._recording_part = self._recording.popleft()

        self.next_part = MethodType(next_part, self, self.__class__)

        def stop(self):
            self._test_case.assertEqual(test_data['results'], self._output.getvalue())

        self.stop = MethodType(stop, self, self.__class__)

    def record(self, path):

        self._output = BytesIO()
        self._recording = deque()
        self._recording_part = OrderedDict()
        self._recording.append(self._recording_part)

        def get(self, method, *args, **kwargs):
            result = method(*args, **kwargs)
            part = self._recording_part
            key = method.__name__
            try:
                results = part[key]
            except KeyError:
                part[key] = results = deque()
            results.append(result)
            return result

        self.get = MethodType(get, self, self.__class__)

        def next_part(self):
            part = OrderedDict()
            self._recording_part = part
            self._recording.append(part)

        self.next_part = MethodType(next_part, self, self.__class__)

        def stop(self):
            with io.open(path, 'wb') as f:
                test = OrderedDict((('inputs', self._recording), ('results', self._output.getvalue())))
                pickle.dump(test, f)

        self.stop = MethodType(stop, self, self.__class__)


def recorded(method):

    @wraps(method)
    def _record(*args, **kwargs):
        return args[0].recorder.get(method, *args, **kwargs)

    return _record


class Test:

    def __init__(self, fieldnames, data_generators):

        TestCase.__init__(self)
        self._data_generators = list(chain((lambda: self._serial_number, time), data_generators))
        self._fieldnames = list(chain(('_serial', '_time'), fieldnames))
        self._recorder = TestRecorder(self)
        self._serial_number = None

    @property
    @recorded
    def fieldnames(self):
        return self._fieldnames

    @property
    @recorded
    def row(self):
        return [data_generator.__call__() for data_generator in self._data_generators]

    @property
    def recorder(self):
        return self._recorder

    @property
    def serial_number(self):
        return self._serial_number

    def playback(self):
        self.recorder.playback(os.path.join(TestInternals._package_path, 'TestRecorder.recording'))
        self._run()
        self.recorder.stop()

    def record(self):
        self.recorder.record(os.path.join(TestInternals._package_path, 'TestRecorder.recording'))
        self._run()
        self.recorder.stop()

    def runTest(self):
        pass  # We'll adopt the new test recording mechanism a little later

    def _run(self):

        writer = RecordWriterV2(self.recorder.output, maxresultrows=10)
        write_record = writer.write_record
        names = self.fieldnames

        for self._serial_number in range(0, 31):
            record = OrderedDict(list(zip(names, self.row)))
            write_record(record)


# test = Test(['random_bytes', 'random_unicode'], [random_bytes, random_unicode])
# test.record()
# test.playback()

Test.__test__ = False
TestRecorder.__test__ = False


if __name__ == "__main__":
    main()
