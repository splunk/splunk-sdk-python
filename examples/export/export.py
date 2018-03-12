#!/usr/bin/env python
#
# Copyright 2012 Splunk, Inc.
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

"""
This software exports a splunk index using the streaming export endpoint
using a parameterized chunking mechanism.
"""

# installation support files
from __future__ import absolute_import
from __future__ import print_function
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import time
from os import path

# splunk support files
from splunklib.binding import connect
try:
    from utils import parse
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

# hidden file
OUTPUT_FILE = "./export.out"
OUTPUT_MODE = "xml"
OUTPUT_MODES = ["csv", "xml", "json"]

CLIRULES = {
   'end': {
        'flags': ["--endtime"],
        'default': "",
        'help': "Start time of export (default is start of index)"
   },
   'index': {
        'flags': ["--index"],
        'default': "*",
        'help': "Index to export (default is all user defined indices)"
   },
   'omode': {
        'flags': ["--omode"],
        'default': OUTPUT_MODE,
        'help': "output format %s default is %s" % (OUTPUT_MODES, OUTPUT_MODE)
   },
   'output': {
        'flags': ["--output"],
        'default': OUTPUT_FILE,
        'help': "Output file name (default is %s)" % OUTPUT_FILE
   },
   'recover': {
        'flags': ["--recover"],
        'default': False,
        'help': "Export attempts to recover from end of existing export"
   },
   'search': {
        'flags': ["--search"],
        'default': "search *",
        'help': "search string (default 'search *')"
   },
   'start': {
        'flags': ["--starttime"],
        'default': "",
        'help': "Start time of export (default is start of index)"
   }
}

def get_csv_next_event_start(location, event_buffer):
    """ determin the event start and end of *any* valid event """

    start = -1
    end = -1

    event_start = event_buffer.find("\n", location + 1)
    event_end = event_buffer.find('"\n', event_start + 1)

    while (event_end > 0):
        parts = event_buffer[event_start:event_end].split(",")
        # test parts 0 and 1 of CSV. Format should be time.qqq, anything
        # else is not time stamp to keep moving.
        try:
            int(parts[0].replace('\n',""))
            timestamp = parts[1].replace('"', "")
            timeparts = timestamp.split('.')
            int(timeparts[0])
            int(timeparts[1])
            return (event_start, event_end)
        except:
            event_start = event_buffer.find("\n", event_end + 2)
            event_end = event_buffer.find('"\n', event_start + 1)

    return (start, end)

def get_csv_event_start(event_buffer):
    """ get the event start of an event that is different (in time)from the
        adjoining event, in CSV format """

    (start, end) = get_csv_next_event_start(0, event_buffer)
    if start < 0:
        return (-1, -1, "")

    print(event_buffer[start:end])

    tstart = event_buffer.find(",", start)
    tend = event_buffer.find(",", tstart+1)
    print(event_buffer[tstart:tend])
    last_time = event_buffer[tstart+1:tend].replace('"',"")

    while end > 0:
        (start, end) = get_csv_next_event_start(start, event_buffer)
        if end < 0:
            return (-1, -1, "")
        tstart = event_buffer.find(",", start)
        tend = event_buffer.find(",", tstart+1)
        this_time = event_buffer[tstart+1:tend].replace('"',"")
        if this_time != last_time:
            return (start, end + 1, last_time)

    return (-1, -1, "")

def get_xml_event_start(event_buffer):
    """ get the event start of an event that is different (in time)from the
        adjoining event, in XML format """

    result_pattern = "<result offset='"
    time_key_pattern = "<field k='_time'>"
    time_start_pattern = "<value><text>"
    time_end_pattern = "<"
    event_end_pattern = "</result>"

    event_start = event_buffer.find(result_pattern)
    event_end = event_buffer.find(event_end_pattern, event_start) + \
                len(event_end_pattern)
    if event_end < 0:
        return (-1, -1, "")
    time_key_start = event_buffer.find(time_key_pattern, event_start)
    time_start = event_buffer.find(time_start_pattern, time_key_start) + \
                 len(time_start_pattern)
    time_end = event_buffer.find(time_end_pattern, time_start + 1)
    last_time = event_buffer[time_start:time_end]

    # wallk through events until time changes
    event_start = event_end
    while event_end > 0:
        event_start = event_buffer.find(result_pattern, event_start + 1)
        event_end = event_buffer.find(event_end_pattern, event_start) + \
                    len(event_end_pattern)
        if event_end < 0:
            return (-1, -1, "")
        time_key_start = event_buffer.find(time_key_pattern, event_start)
        time_start = event_buffer.find(time_start_pattern, time_key_start)
        time_end = event_buffer.find(time_end_pattern, time_start)
        this_time = event_buffer[time_start:time_end]
        if this_time != last_time:
            return (event_start, event_end, last_time)
        event_start = event_end

    return (-1, -1, "")

def get_json_event_start(event_buffer):
    """ get the event start of an event that is different (in time)from the
        adjoining event, in XML format """

    event_start_pattern = '{"_cd":"'
    time_key_pattern = '"_time":"'
    time_end_pattern = '"'
    event_end_pattern = '"},\n'
    event_end_pattern2 = '"}[]' # old json output format bug

    event_start = event_buffer.find(event_start_pattern)
    event_end = event_buffer.find(event_end_pattern, event_start) + \
                len(event_end_pattern)
    if event_end < 0:
        event_end = event_buffer.find(event_end_pattern2, event_start) + \
                    len(event_end_pattern2)
    if (event_end < 0):
        return (-1, -1, "")

    time_start = event_buffer.find(time_key_pattern, event_start) + \
                 len(time_key_pattern)
    time_end = event_buffer.find(time_end_pattern, time_start + 1)
    last_time = event_buffer[time_start:time_end]

    event_start = event_end
    while event_end > 0:
        event_start = event_buffer.find(event_start_pattern, event_start + 1)
        event_end = event_buffer.find(event_end_pattern, event_start) + \
                    len(event_end_pattern)
        if event_end < 0:
            event_end = event_buffer.find(event_end_pattern2, event_start) + \
                        len(event_end_pattern2)
        if (event_end < 0):
            return (-1, -1, "")
        time_start = event_buffer.find(time_key_pattern, event_start) + \
                     len(time_key_pattern)
        time_end = event_buffer.find(time_end_pattern, time_start + 1)
        this_time = event_buffer[time_start:time_end]
        if this_time != last_time:
            return (event_start-2, event_end, last_time)
        event_start = event_end

    return (-1, -1, "")

def get_event_start(event_buffer, event_format):
    """ dispatch event start method based on event format type """

    if event_format == "csv":
        return get_csv_event_start(event_buffer)
    elif event_format == "xml":
        return get_xml_event_start(event_buffer)
    else:
        return get_json_event_start(event_buffer)

def recover(options):
    """ recover from an existing export run. We do this by
        finding the last time change between events, truncate the file
        and restart from there """

    event_format = options.kwargs['omode']

    buffer_size = 64*1024
    fpd = open(options.kwargs['output'], "r+")
    fpd.seek(0, 2) # seek to end
    fptr = max(fpd.tell() - buffer_size, 0)
    fptr_eof = 0

    while (fptr > 0):
        fpd.seek(fptr)
        event_buffer = fpd.read(buffer_size)
        (event_start, next_event_start, last_time) = \
            get_event_start(event_buffer, event_format)
        if (event_start != -1):
            fptr_eof = event_start + fptr
            break
        fptr = fptr - buffer_size

    if fptr < 0:
        # didn't find a valid event, so start over
        fptr_eof = 0
        last_time = 0 

    # truncate file here
    fpd.truncate(fptr_eof)
    fpd.seek(fptr_eof)
    fpd.write("\n")
    fpd.close()

    return last_time

def cleanup_tail(options):
    """ cleanup the tail of a recovery """

    if options.kwargs['omode'] == "csv":
        options.kwargs['fd'].write("\n")
    elif options.kwargs['omode'] == "xml":
        options.kwargs['fd'].write("\n</results>\n")
    else:
        options.kwargs['fd'].write("\n]\n")

def export(options, service):
    """ main export method: export any number of indexes """

    start = options.kwargs['start']
    end = options.kwargs['end']
    fixtail = options.kwargs['fixtail']
    once = True

    squery = options.kwargs['search']
    squery = squery + " index=%s" % options.kwargs['index']
    if (start != ""):
        squery = squery + " earliest_time=%s" % start
    if (end != ""):
        squery = squery + " latest_time=%s" % end

    success = False

    while not success:
        # issue query to splunkd
        # count=0 overrides the maximum number of events
        # returned (normally 50K) regardless of what the .conf
        # file for splunkd says. 
        result = service.get('search/jobs/export', 
                             search=squery, 
                             output_mode=options.kwargs['omode'],
                             timeout=60,
                             earliest_time="0.000",
                             time_format="%s.%Q",
                             count=0)

        if result.status != 200:
            print("warning: export job failed: %d, sleep/retry" % result.status)
            time.sleep(60)
        else:
            success = True

    # write export file 
    while True:
        if fixtail and once:
            cleanup_tail(options)
            once = False
        content = result.body.read()
        if len(content) == 0: break
        options.kwargs['fd'].write(content)
        options.kwargs['fd'].write("\n")

    options.kwargs['fd'].flush()

def main():
    """ main entry """
    options = parse(sys.argv[1:], CLIRULES, ".splunkrc")

    if options.kwargs['omode'] not in OUTPUT_MODES:
        print("output mode must be one of %s, found %s" % (OUTPUT_MODES,
              options.kwargs['omode']))
        sys.exit(1)

    service = connect(**options.kwargs)

    if path.exists(options.kwargs['output']):
        if not options.kwargs['recover']:
            print("Export file %s exists, and recover option nor specified" % \
                  options.kwargs['output'])
            sys.exit(1)
        else:
            options.kwargs['end'] = recover(options)
            options.kwargs['fixtail'] = True
            openmode = "a"
    else:
        openmode = "w"
        options.kwargs['fixtail'] = False
        
    try:
        options.kwargs['fd'] = open(options.kwargs['output'], openmode)
    except IOError:
        print("Failed to open output file %s w/ mode %s" % \
                             (options.kwargs['output'], openmode))
        sys.exit(1)

    export(options, service)

if __name__ == '__main__':
    main()
