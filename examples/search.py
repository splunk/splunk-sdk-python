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

"""A command line utility for executing Splunk searches."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from time import sleep

from splunklib.binding import HTTPError
import splunklib.client as client

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

FLAGS_TOOL = [ "verbose" ]

FLAGS_CREATE = [
    "earliest_time", "latest_time", "now", "time_format",
    "exec_mode", "search_mode", "rt_blocking", "rt_queue_size",
    "rt_maxblocksecs", "rt_indexfilter", "id", "status_buckets",
    "max_count", "max_time", "timeout", "auto_finalize_ec", "enable_lookups",
    "reload_macros", "reduce_freq", "spawn_process", "required_field_list",
    "rf", "auto_cancel", "auto_pause",
]

FLAGS_RESULTS = [
    "offset", "count", "search", "field_list", "f", "output_mode"
]

def cmdline(argv, flags, **kwargs):
    """A cmdopts wrapper that takes a list of flags and builds the
       corresponding cmdopts rules to match those flags."""
    rules = dict([(flag, {'flags': ["--%s" % flag]}) for flag in flags])
    return parse(argv, rules, ".splunkrc", **kwargs)

def main(argv):
    usage = 'usage: %prog [options] "search"'

    flags = []
    flags.extend(FLAGS_TOOL)
    flags.extend(FLAGS_CREATE)
    flags.extend(FLAGS_RESULTS)
    opts = cmdline(argv, flags, usage=usage)

    if len(opts.args) != 1:
        error("Search expression required", 2)
    search = opts.args[0]

    verbose = opts.kwargs.get("verbose", 0)

    kwargs_splunk = dslice(opts.kwargs, FLAGS_SPLUNK)
    kwargs_create = dslice(opts.kwargs, FLAGS_CREATE)
    kwargs_results = dslice(opts.kwargs, FLAGS_RESULTS)

    service = client.connect(**kwargs_splunk)

    try:
        service.parse(search, parse_only=True)
    except HTTPError as e:
        cmdopts.error("query '%s' is invalid:\n\t%s" % (search, e.message), 2)
        return

    job = service.jobs.create(search, **kwargs_create)
    while True:
        while not job.is_ready():
            pass
        stats = {'isDone': job['isDone'],
                 'doneProgress': job['doneProgress'],
                 'scanCount': job['scanCount'],
                 'eventCount': job['eventCount'],
                 'resultCount': job['resultCount']}
        progress = float(stats['doneProgress'])*100
        scanned = int(stats['scanCount'])
        matched = int(stats['eventCount'])
        results = int(stats['resultCount'])
        if verbose > 0:
            status = ("\r%03.1f%% | %d scanned | %d matched | %d results" % (
                progress, scanned, matched, results))
            sys.stdout.write(status)
            sys.stdout.flush()
        if stats['isDone'] == '1': 
            if verbose > 0: sys.stdout.write('\n')
            break
        sleep(2)

    if not kwargs_results.has_key('count'): kwargs_results['count'] = 0
    results = job.results(**kwargs_results)
    while True:
        content = results.read(1024)
        if len(content) == 0: break
        sys.stdout.write(content)
        sys.stdout.flush()
    sys.stdout.write('\n')

    job.cancel()

if __name__ == "__main__":
    main(sys.argv[1:])
