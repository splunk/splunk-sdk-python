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

from tests.modularinput.modularinput_testlib import unittest, xml_compare, data_open
from splunklib.modularinput.event import Event, ET
from splunklib.modularinput.event_writer import EventWriter

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class EventTestCase(unittest.TestCase):
    def test_event_without_enough_fields_fails(self):
        """Check that events without data throw an error"""
        with self.assertRaises(ValueError):
            event = Event()
            stream = StringIO()
            event.write_to(stream)
        self.assertTrue(True)

    def test_xml_of_event_with_minimal_configuration(self):
        """Generate XML from an event object with a small number of fields,
        and see if it matches what we expect."""
        stream = StringIO()

        event = Event(
            data="This is a test of the emergency broadcast system.",
            stanza="fubar",
            time="%.3f" % 1372187084.000
        )

        event.write_to(stream)

        constructed = ET.fromstring(stream.getvalue())
        expected = ET.parse(data_open("data/event_minimal.xml")).getroot()

        self.assertTrue(xml_compare(expected, constructed))

    def test_xml_of_event_with_more_configuration(self):
        """Generate XML from an even object with all fields set, see if
        it matches what we expect"""
        stream = StringIO()

        event = Event(
            data="This is a test of the emergency broadcast system.",
            stanza="fubar",
            time="%.3f" % 1372274622.493,
            host="localhost",
            index="main",
            source="hilda",
            sourcetype="misc",
            done=True,
            unbroken=True
        )
        event.write_to(stream)

        constructed = ET.fromstring(stream.getvalue())
        expected = ET.parse(data_open("data/event_maximal.xml")).getroot()

        self.assertTrue(xml_compare(expected, constructed))

    def test_writing_events_on_event_writer(self):
        """Write a pair of events with an EventWriter, and ensure that they
        are being encoded immediately and correctly onto the output stream"""
        out = StringIO()
        err = StringIO()

        ew = EventWriter(out, err)

        e = Event(
            data="This is a test of the emergency broadcast system.",
            stanza="fubar",
            time="%.3f" % 1372275124.466,
            host="localhost",
            index="main",
            source="hilda",
            sourcetype="misc",
            done=True,
            unbroken=True
        )
        ew.write_event(e)

        found = ET.fromstring("%s</stream>" % out.getvalue())
        expected = ET.parse(data_open("data/stream_with_one_event.xml")).getroot()

        self.assertTrue(xml_compare(expected, found))
        self.assertEqual(err.getvalue(), "")

        ew.write_event(e)
        ew.close()

        found = ET.fromstring(out.getvalue())
        expected = ET.parse(data_open("data/stream_with_two_events.xml")).getroot()

        self.assertTrue(xml_compare(expected, found))

    def test_error_in_event_writer(self):
        """An event which cannot write itself onto an output stream
        (such as because it doesn't have a data field set)
        should write an error. Check that it does so."""
        out = StringIO()
        err = StringIO()

        ew = EventWriter(out, err)
        e = Event()
        try:
            ew.write_event(e)
            self.assertTrue(False)
        except ValueError as e:
            self.assertEqual("Events must have at least the data field set to be written to XML.", str(e))

    def test_logging_errors_with_event_writer(self):
        """Check that the log method on EventWriter produces the
        expected error message."""
        out = StringIO()
        err = StringIO()

        ew = EventWriter(out, err)

        ew.log(EventWriter.ERROR, "Something happened!")

        self.assertEqual("ERROR Something happened!\n", err.getvalue())

    def test_write_xml_is_sane(self):
        """Check that EventWriter.write_xml_document writes sensible
        XML to the output stream."""
        out = StringIO()
        err = StringIO()

        ew = EventWriter(out, err)

        expected_xml = ET.parse(data_open("data/event_maximal.xml")).getroot()

        ew.write_xml_document(expected_xml)
        found_xml = ET.fromstring(out.getvalue())

        self.assertTrue(xml_compare(expected_xml, found_xml))

if __name__ == "__main__":
    unittest.main()