#!/usr/bin/env python
#
# Copyright © 2011-2024 Splunk, Inc.
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


import re
import sys
from io import StringIO

import pytest

from tests.unit.modularinput.modularinput_testlib import xml_compare, data_open
from splunklib.modularinput.event import Event, ET
from splunklib.modularinput.event_writer import EventWriter


def test_event_without_enough_fields_fails(capsys):
    """Check that events without data throw an error"""
    with pytest.raises(ValueError), capsys.disabled():
        event = Event()
        event.write_to(sys.stdout)


def test_xml_of_event_with_minimal_configuration(capsys):
    """Generate XML from an event object with a small number of fields,
    and see if it matches what we expect."""

    event = Event(
        data="This is a test of the emergency broadcast system.",
        stanza="fubar",
        time="%.3f" % 1372187084.000,
    )

    event.write_to(sys.stdout)

    captured = capsys.readouterr()
    constructed = ET.fromstring(captured.out)
    with data_open("data/event_minimal.xml") as data:
        expected = ET.parse(data).getroot()

        assert xml_compare(expected, constructed)


def test_xml_of_event_with_more_configuration(capsys):
    """Generate XML from an even object with all fields set, see if
    it matches what we expect"""

    event = Event(
        data="This is a test of the emergency broadcast system.",
        stanza="fubar",
        time="%.3f" % 1372274622.493,
        host="localhost",
        index="main",
        source="hilda",
        sourcetype="misc",
        done=True,
        unbroken=True,
    )
    event.write_to(sys.stdout)

    captured = capsys.readouterr()

    constructed = ET.fromstring(captured.out)
    with data_open("data/event_maximal.xml") as data:
        expected = ET.parse(data).getroot()

        assert xml_compare(expected, constructed)


def test_writing_events_on_event_writer(capsys):
    """Write a pair of events with an EventWriter, and ensure that they
    are being encoded immediately and correctly onto the output stream"""

    ew = EventWriter(sys.stdout, sys.stderr)

    e = Event(
        data="This is a test of the emergency broadcast system.",
        stanza="fubar",
        time="%.3f" % 1372275124.466,
        host="localhost",
        index="main",
        source="hilda",
        sourcetype="misc",
        done=True,
        unbroken=True,
    )
    ew.write_event(e)

    captured = capsys.readouterr()

    first_out_part = captured.out

    with data_open("data/stream_with_one_event.xml") as data:
        found = ET.fromstring(f"{first_out_part}</stream>")
        expected = ET.parse(data).getroot()

        assert xml_compare(expected, found)
        assert captured.err == ""

    ew.write_event(e)
    ew.close()

    captured = capsys.readouterr()
    with data_open("data/stream_with_two_events.xml") as data:
        found = ET.fromstring(first_out_part + captured.out)
        expected = ET.parse(data).getroot()

        assert xml_compare(expected, found)


def test_error_in_event_writer():
    """An event which cannot write itself onto an output stream
    (such as because it doesn't have a data field set)
    should write an error. Check that it does so."""

    ew = EventWriter(sys.stdout, sys.stderr)
    e = Event()
    with pytest.raises(ValueError) as excinfo:
        ew.write_event(e)
    assert (
        str(excinfo.value)
        == "Events must have at least the data field set to be written to XML."
    )


def test_logging_errors_with_event_writer(capsys):
    """Check that the log method on EventWriter produces the
    expected error message."""

    ew = EventWriter(sys.stdout, sys.stderr)

    ew.log(EventWriter.ERROR, "Something happened!")

    captured = capsys.readouterr()
    assert captured.err == "ERROR Something happened!\n"


def test_write_xml_is_sane(capsys):
    """Check that EventWriter.write_xml_document writes sensible
    XML to the output stream."""

    ew = EventWriter(sys.stdout, sys.stderr)

    with data_open("data/event_maximal.xml") as data:
        expected_xml = ET.parse(data).getroot()

        ew.write_xml_document(expected_xml)
        captured = capsys.readouterr()
        found_xml = ET.fromstring(captured.out)

        assert xml_compare(expected_xml, found_xml)


def test_log_exception():
    out, err = StringIO(), StringIO()
    ew = EventWriter(out, err)

    exc = Exception("Something happened!")

    try:
        raise exc
    except Exception:
        ew.log_exception("ex1")

    assert out.getvalue() == ""

    # Remove paths and line
    err = re.sub(r'File "[^"]+', 'File "...', err.getvalue())
    err = re.sub(r"line \d+", "line 123", err)

    # One line
    assert err == (
        "ERROR ex1 - Traceback (most recent call last): "
        '  File "...", line 123, in test_log_exception '
        "    raise exc "
        "Exception: Something happened! "
    )
