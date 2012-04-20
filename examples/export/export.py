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

"""
This software exports a splunk index using the streaming export endpoint
using a parameterized chunking mechanism.
"""

# installation support files
import sys
import operator
import time
import os

# splunk support files
import splunklib.binding as binding
from splunklib.binding import connect
from utils import parse

# hidden file
RESTART_FILE = "./.export_restart_log"
OUTPUT_FILE = "./export.out"
REQUEST_LIMIT = 100000
OUTPUT_MODE = "xml"
OUTPUT_MODES = ["csv", "xml", "json"]
RETRY_LIMIT = 500

CLIRULES = {
   'index': {
        'flags': ["--index"],
        'default': "*",
        'help': "Index to export (default is all user defined indices)"
    },
   'progress': {
        'flags': ["--progress"],
        'default': False,
        'help': "display processing progress"
    },
   'start': {
        'flags': ["--starttime"],
        'default': 0,
        'help': "Start time of export (default is start of index)"
    },
   'end': {
        'flags': ["--endtime"],
        'default': 0,
        'help': "Start time of export (default is start of index)"
    },
   'output': {
        'flags': ["--output"],
        'default': OUTPUT_FILE,
        'help': "Output file name (default is %s)" % OUTPUT_FILE
    },
   'limit': {
        'flags': ["--limit"],
        'default': REQUEST_LIMIT,
        'help': "Events per request limit (default is %d)" % REQUEST_LIMIT
    },
   'omode': {
        'flags': ["--omode"],
        'default': OUTPUT_MODE,
        'help': "output format %s default is %s" % (OUTPUT_MODES, OUTPUT_MODE)
    },
   'restart': {
        'flags': ["--restart"],
        'default': False,
        'help': "Restarts an existing export that was prematurely terminated"
    },
}

def query(context, start, end, span, index):
    """ query the server for a specific range of events """

    # generate a search
    squery = "search * index=%s " % index

    # if start/end specified, use them
    if start != 0:
        squery = squery + "earliest_time=%d " % start
    if end != 0:
        squery = squery + "latest_time=%d " % end

    # span is in seconds for buckets
    squery = squery + "| timechart "

    if span == 86400:
        # force splunk into 12:00:00AM start time for buckets.
        squery = squery + "span=1d "
    else:
        squery = squery + "span=%ds " % span

    squery = squery + "count"

    retry = True
    while retry:
        result = context.get('search/jobs/export', search=squery, 
                              output_mode="csv", time_format="%s")
        if result.status != 200:
            print "Failed to get event counts, HTTP status=%d, retrying"\
                   % result.status
            time.sleep(10)
        else:
            retry = False

    # generate a list of lines from teh csv return data
    lines = result.body.read().splitlines()
    if len(lines) == 0:
        return []

    return lines

def get_buckets(context, start, end, index, limit, span):
    """ generate an export to splunkd for the index
        elememnts within the given time range """

    # time downsampling ratio day:hour, hour:minute, minute:second
    # the initial time span is 1 day (86400 seconds) -- if the number
    # of events is too large, break down the day into hours, repeat
    # as necessary to minutes and then to seconds.
    #
    # We do this to make a reasonable amount of data transfer for each
    # request when we export the data and it allows for fine grained 
    # restart on errors.
    # 
    # also because splunk "snaps" events based on the span size, this
    # behavior requires span and start/end times to be fully in phase
    # (i.e. starttime modulo span == 0).
    downsample = { 86400 : 3600, 3600 : 60, 60 : 1 }

    # trace/debug
    #print 'start=%d, end=%d, index=%s, maxevents=%d, timespan=%d' % \
    #      (start, end, index, limit, span)

    lines = query(context, start, end, span, index)
    if len(lines) == 0:
        return []

    # strip out line 0: Line 0 is the header info
    # which contains the text: 
    #     count,"_time","_span", ["_spandays"]
    lines.remove(lines[0])

    buckets = []

    # parse the lines returned from splunk. They are in the form
    # eventcount,starttime,timequantum
    for line in lines:
        elements = line.split(",")
        # extract the element components
        enumevents = int(elements[0])
        estarttime = int(elements[1])
        espan = int(elements[2])

        # if the numnber of events in this bucket is larger than
        # our limit, we need to break them up (cut in half).
        if enumevents > limit:
            # only split down to one second.
            if span > 1:
                # get next smaller chunk.
                newspan = downsample[span]

                # make smaller buckets, recurse with smaller span.
                endtime = estarttime + span
                expanded = get_buckets(context, estarttime, endtime, 
                                       index, limit, newspan)
                # flatten list and put into current list.
                for bucket in expanded:
                    buckets.append(bucket)
            else:
                # can't get any smaller than 1 second interval.
                buckets.append((enumevents, estarttime, espan))
        else:
            # add to our list.
            buckets.append((enumevents, estarttime, espan))

    return buckets

def normalize_export_buckets(options, context):
    """ query splunk to get the buckets of events and attempt to normalize """

    # round to nearest 'start of day'
    start = int(options.kwargs['start']) / 86400
    if start != int(options.kwargs['start'])*86400:
        print "INFO: start time rounded down to start of day"
    start = start * 86400

    # start with a bucket size of one day: 86400 seconds.
    buckets = get_buckets(context, start, 
                          int(options.kwargs['end']), 
                          options.kwargs['index'], 
                          int(options.kwargs['limit']), 
                          86400)

    # sort on start time: tuples are (events, starttime, quantum).
    # necessary? probably not...
    buckets = sorted(buckets, key=operator.itemgetter(1)) 

    return buckets

def sanitize_restart_bucket_list(options, bucket_list):
    """ clean up bucket list for an export already in progress """

    sane = True

    ## run through the entries we have already processed found in the restart
    ## file and remove them from the live bucket list.

    # read restart file into a new list.
    rfd = open(RESTART_FILE, "r")
    rslist = []
    plist = []
    for line in rfd:
        line = line[:-1].split(",")
        rslist.append((int(line[0]), int(line[1]), int(line[2])))
    rfd.close()

    for entry in rslist:
        # throw away empty buckets, until a non-empty bucket.
        while bucket_list[0][0] == 0:
            bucket_list.pop(0)

        if bucket_list[0] != entry:
            print "Warning: live list contains: %s, restart list contains: %s" \
                 % (str(bucket_list[0]), str(rslist[0]))
            sane = False

        if options.kwargs['progress']:
            print "restart skipping already handled bucket: %s" % str(entry)

        # append the buckets we have already processed.
        plist.append(bucket_list.pop(0))

    return (plist, bucket_list, sane)

def validate_export(options, bucket_list):
    """ validate an existing export for consistency """

    # open restart file:
    # pbl is processed bucket list, abl is adjusted bucket list.
    (pbl, abl, sane) = sanitize_restart_bucket_list(options, bucket_list)
    if not sane:
        print "Mismatch between restart and live event list"
        return ([], False)

    # open main export for reading
    try:
        efd = open(options.kwargs['output'], 'r')
    except IOError:
        return ([], False)

    ##
    ## abl contains the adjusted bucket list: the things we have 
    ## left to process. What we do now is read the end of the export 
    ## file and validate that it matches the bucket prior to the start 
    ## of the restart file, which is in pbl. 
    ##
    ## pbl is the processed bucket list: the things thart should already 
    ## have been processed and in the export file.
    ##

    # seek to end, read minimum of 64K backwards (?big enough?), or from start
    # (whichever is smaller) of file to get the last bit of the previous 
    # exported file.
    efd.seek(0, 2)
    bytestoread = min(65536, efd.tell())
    efd.seek(efd.tell()-bytestoread)
    endofdata = efd.read(bytestoread)
    efd.close()

    # get the last bucket processed.
    pcount = -1
    ptime = -1
    pdelta = -1
    if len(pbl) != 0:
        pcount = pbl[len(pbl)-1][0]
        ptime = pbl[len(pbl)-1][1]
        pdelta = pbl[len(pbl)-1][2]

    # check the tail end of the data, (in reverse order from the end) in 
    # particular we are looking for the FIRST two fields at the beginning 
    # of a line that matches:
    #  <num>,"time",...
    #
    # N.B.: This may not guarantee a real event boundary and may have to be 
    # revisited with a better heuristic.
    #
    dcount = -1
    dtime = -1
    for line in reversed(endofdata.split("\n")):
        csvdata = line.split(",")
        if len(csvdata) > 1:
            try:
                dcount = int(csvdata[0])
                dtime = int(float(csvdata[1].strip('"')))
                # found last one
                break
            except ValueError:
                # skip and keep walking backwards
                pass
     
    # didn't find any events in exported data, but no processed 
    # buckets either, we are OK.
    if dcount == -1 and pcount == -1:
        return (abl, True)
    # didn't find any events in exported data, but we have at 
    # least one processed bucket, we are not sane.
    elif dcount == -1 and  pcount != -1:
        sane = False
    # found at least one event in exported data, but we have not
    # processed any buckets, we are not sane.
    elif dcount != -1 and pcount == -1:
        sane = False

    if not sane:
        return (abl, False)

    # at this point we have some exported data and we have processed some
    # buckets, make sure that the last event in the exported data, 
    # is the same as the number of events processed in the bucket AND
    # that its event time is within the time range of the processed bucket.
    # If we succeed, then we are sane.
    #
    # note, events in exported data are 0 based in count, and 1 based in 
    # processed count.
    if (dcount + 1) == pcount and dtime <= (ptime + pdelta):
        return (abl, True)

    # not sane.
    return (abl, False)

def report_banner(bucket_list):
    """ output banner for export operation """

    eventcount = 0
    requests = 0

    for bucket in bucket_list:
        if bucket[0] > 0:
            requests += 1
        eventcount += bucket[0]

    print "Events exported: %d, requiring %d splunk fetches" % \
                                            (eventcount, requests)

def export(options, context, bucket_list):
    """ given the buckets, export the events """

    header = False

    report_banner(bucket_list)

    # (re)open restart file appending to the end if it exists.
    rfd = open(RESTART_FILE, "a")

    for bucket in bucket_list:
        if bucket[0] == 0:
            if options.kwargs['progress']:
                print "SKIPPING BUCKET:-------- %s" % str(bucket)
        else:
            retry = True
            retry_count = 0
            while retry:
                if options.kwargs['progress']:
                    print "PROCESSING BUCKET:------ %s" % str(bucket)
                # generate a search.
                squery = "search * index=%s " % options.kwargs['index']

                start = bucket[1]
                quantum = bucket[2]

                squery = squery + "earliest_time=%d " % start
                squery = squery + "latest_time=%d " % (start+quantum)
    
                # issue query to splunkd
                # count=0 overrides the maximum number of events
                # returned (normally 50K) regardless of what the .conf
                # file for splunkd says. 
                result = context.get('search/jobs/export', 
                                 search=squery, 
                                 output_mode=options.kwargs['omode'],
                                 count=0)
                                 #count=int(bucket[0])+1)

                if result.status != 200:
                    retry_count = retry_count + 1
                    if options.kwargs['progress']:
                        print "HTTP status: %d, sleep and retry..." % \
                              result.status

                    if retry_count > RETRY_LIMIT:
                        print "RETRY_LIMIT reached, halting export. you can"
                        print " resume the export at a later date using the"
                        print " --restart flag"
                        return False

                    time.sleep(10)
                else:
                    retry = False

            # write export file 
            # N.B.: atomic writes in python don't seem to exist. In order
            # *really* make this robust, we need to atomically write the 
            # body of the event returned AND update the restart file and
            # guarantee both committed.

            # atomic write start

            data = result.body.read()
            data = data.splitlines()
            if len(data) > 0:
                firstline = data[0]
                data.pop(0)

                # special handling for each output mode
                if options.kwargs['omode'] == "xml":
                    # for xml, always write the first line, which is just an XML
                    # signifier
                    options.kwargs['fd'].write(firstline)
                    options.kwargs['fd'].write("\n")
                elif options.kwargs['omode'] == "csv":
                    # for csv, only print out the field specifier once
                    if not header:
                        options.kwargs['fd'].write(firstline)
                        options.kwargs['fd'].write("\n")
                        header = True
                # for json, we never print out the first line which is always
                # an empty/dangling bracket "["

                for line in data:
                    options.kwargs['fd'].write(line)
                    options.kwargs['fd'].write("\n")

                options.kwargs['fd'].flush()

            rfd.write(str(bucket).strip("(").strip(")").replace(" ",""))
            rfd.write("\n")
            rfd.flush()
            # atomic write commit

    return True

def main():
    """ main entry """

    # perform idmpotent login/connect -- get login creds from ~/.splunkrc
    # if not specified in the command line arguments.
    options = parse(sys.argv[1:], CLIRULES, ".splunkrc")

    if options.kwargs['omode'] not in OUTPUT_MODES:
        print "output mode must be one of %s, found %s" % (OUTPUT_MODES,
              options.kwargs['omode'])
        sys.exit(1)

    # minor sanity check on start/end time
    try:
        int(options.kwargs['start'])
        int(options.kwargs['end'])
    except ValueError:
        print "ERROR: start and end times most be expressed as an integer."
        print "       An integer that represents seconds from 1970."
        sys.exit(1)

    connection = connect(**options.kwargs)

    # get lower level context.
    context = binding.connect( host=connection.host, 
                               username=connection.username,
                               password=connection.password)

    # open restart file.
    rfd = None
    try:
        rfd = open(RESTART_FILE, "r")
    except IOError:
        pass

    # check request and environment for sanity.
    if options.kwargs['restart'] is not False and rfd is None:
        print "Failed to open restart file %s for reading" % RESTART_FILE
        sys.exit(1)
    elif options.kwargs['restart'] is False and rfd is not None:
        print "Warning: restart file %s exists." % RESTART_FILE
        print "         manually remove this file to continue complete export"
        print "         or use --restart=1 to continue export"
        sys.exit(1)
    else:
        pass

    # close restart file.
    if rfd is not None:
        rfd.close()

    # normalize buckets to contain no more than "limit" events per bucket
    # however, there may be a situation where there will be more events in 
    # our smallest bucket (one second) -- but there is not much we are going
    # to do about it.
    bucket_list = normalize_export_buckets(options, context)

    #
    # if we have a restart in progress, we should spend some time to validate
    # the export by examining the last bit of the exported file versus the 
    # restart log we have so far.
    #
    if options.kwargs['restart'] is not False:
        (bucket_list, sane) = validate_export(options, bucket_list)
        if sane is False:
            print "Failed to validate export, consistency check failed"
            sys.exit(1)

    # open export for writing, unless we are restarting the export,
    # In which case we append to the export.
    mode = "w"
    if options.kwargs['restart'] is not False:
        mode = "a"

    try:
        options.kwargs['fd'] = open(options.kwargs['output'], mode)
    except IOError:
        print "Failed to open output file %s w/ mode %s" % \
                             (options.kwargs['output'], mode)
        sys.exit(1)

    # chunk through each bucket, and on success, remove the restart file.
    if export(options, context, bucket_list) is True:
        os.remove(RESTART_FILE)

if __name__ == '__main__':
    main()
