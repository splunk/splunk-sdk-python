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

"""A command line utility for interacting with Splunk search jobs."""

# All job commands operate on search 'specifiers' (spec). A search specifier
# is either a search-id (sid) or the index of the search job in the list of
# jobs, eg: @0 would specify the frist job in the list, @1 the second, and so
# on.

from pprint import pprint
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from splunklib.client import connect
try:
    from utils import error, parse, cmdline
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

HELP_EPILOG = """
Commands:            
    cancel <search>+
    create <query> [options]
    events <search>+
    finalize <search>+
    list [<search>]*
    pause <search>+
    preview <search>+
    results <search>+
    searchlog <search>+
    summary <search>+
    perf <search>+
    timeline <search>+
    touch <search>+
    unpause <search>+

A search can be specified either by using it 'search id' ('sid'), or by
using the index in the listing of searches. For example, @5 would refer
to the 5th search job in the list.

Examples:
    # Cancel a search
    job.py cancel @0

    # Create a search
    job.py create 'search * | stats count' --search_mode=blocking

    # List all searches
    job.py list

    # List properties of the specified searches
    job.py list @3 scheduler__nobody__search_SW5kZXhpbmcgd29ya2xvYWQ_at_1311888600_b18031c8d8f4b4e9

    # Get all results for the third search
    job.py results @3
"""

FLAGS_CREATE = [
    "search", "earliest_time", "latest_time", "now", "time_format",
    "exec_mode", "search_mode", "rt_blocking", "rt_queue_size",
    "rt_maxblocksecs", "rt_indexfilter", "id", "status_buckets",
    "max_count", "max_time", "timeout", "auto_finalize_ec", "enable_lookups",
    "reload_macros", "reduce_freq", "spawn_process", "required_field_list",
    "rf", "auto_cancel", "auto_pause",
]

FLAGS_EVENTS = [
    "offset", "count", "earliest_time", "latest_time", "search",
    "time_format", "output_time_format", "field_list", "f", "max_lines",
    "truncation_mode", "output_mode", "segmentation"
]

FLAGS_RESULTS = [
    "offset", "count", "search", "field_list", "f", "output_mode"
]

FLAGS_TIMELINE = [
    "time_format", "output_time_format"
]

FLAGS_SEARCHLOG = [
    "attachment"
]

FLAGS_SUMMARY = [
    "earliest_time", "latest_time", "time_format", "output_time_format",
    "field_list", "f", "search", "top_count", "min_freq"
]

def cmdline(argv, flags):
    """A cmdopts wrapper that takes a list of flags and builds the
       corresponding cmdopts rules to match those flags."""
    rules = dict([(flag, {'flags': ["--%s" % flag]}) for flag in flags])
    return parse(argv, rules)

def output(stream):
    """Write the contents of the given stream to stdout."""
    while True:
        content = stream.read(1024)
        if len(content) == 0: break
        sys.stdout.write(content)

class Program:
    def __init__(self, service):
        self.service = service

    def cancel(self, argv):
        self.foreach(argv, lambda job: job.cancel())

    def create(self, argv):
        """Create a search job."""
        opts = cmdline(argv, FLAGS_CREATE)
        if len(opts.args) != 1:
            error("Command requires a search expression", 2)
        query = opts.args[0]
        job = self.service.jobs.create(opts.args[0], **opts.kwargs)
        print job.sid

    def events(self, argv):
        """Retrieve events for the specified search jobs."""
        opts = cmdline(argv, FLAGS_EVENTS)
        self.foreach(opts.args, lambda job: 
            output(job.events(**opts.kwargs)))

    def finalize(self, argv):
        """Finalize the specified search jobs."""
        self.foreach(argv, lambda job: job.finalize())

    def foreach(self, argv, func):
        """Apply the function to each job specified in the argument vector."""
        if len(argv) == 0:
            error("Command requires a search specifier.", 2)
        for item in argv:
            job = self.lookup(item)
            if job is None:
                error("Search job '%s' does not exist" % item, 2)
            func(job)

    def list(self, argv):
        """List all current search jobs if no jobs specified, otherwise
           list the properties of the specified jobs."""

        def read(job):
            for key in sorted(job.content.keys()):
                # Ignore some fields that make the output hard to read and
                # that are available via other commands.
                if key in ["performance"]: continue
                print "%s: %s" % (key, job.content[key])

        if len(argv) == 0:
            index = 0
            for job in self.service.jobs:
                print "@%d : %s" % (index, job.sid)
                index += 1
            return

        self.foreach(argv, read)

    def preview(self, argv):
        """Retrieve the preview for the specified search jobs."""
        opts = cmdline(argv, FLAGS_RESULTS)
        self.foreach(opts.args, lambda job: 
            output(job.preview(**opts.kwargs)))

    def results(self, argv):
        """Retrieve the results for the specified search jobs."""
        opts = cmdline(argv, FLAGS_RESULTS)
        self.foreach(opts.args, lambda job: 
            output(job.results(**opts.kwargs)))

    def sid(self, spec):
        """Convert the given search specifier into a search-id (sid)."""
        if spec.startswith('@'):
            index = int(spec[1:])
            jobs = self.service.jobs.list()
            if index < len(jobs):
                return jobs[index].sid
        return spec # Assume it was already a valid sid
        
    def lookup(self, spec):
        """Lookup search job by search specifier."""
        return self.service.jobs[self.sid(spec)]

    def pause(self, argv):
        """Pause the specified search jobs."""
        self.foreach(argv, lambda job: job.pause())

    def perf(self, argv):
        """Retrive performance info for the specified search jobs."""
        self.foreach(argv, lambda job: pprint(job['performance']))

    def run(self, argv):
        """Dispatch the given command."""
        command = argv[0]
        handlers = { 
            'cancel': self.cancel,
            'create': self.create,
            'events': self.events,
            'finalize': self.finalize,
            'list': self.list,
            'pause': self.pause,
            'preview': self.preview,
            'results': self.results,
            'searchlog': self.searchlog,
            'summary': self.summary,
            'perf': self.perf,
            'timeline': self.timeline,
            'touch': self.touch,
            'unpause': self.unpause,
        }
        handler = handlers.get(command, None)
        if handler is None:
            error("Unrecognized command: %s" % command, 2)
        handler(argv[1:])

    def searchlog(self, argv):
        """Retrieve the searchlog for the specified search jobs."""
        opts = cmdline(argv, FLAGS_SEARCHLOG)
        self.foreach(opts.args, lambda job: 
            output(job.searchlog(**opts.kwargs)))

    def summary(self, argv):
        opts = cmdline(argv, FLAGS_SUMMARY)
        self.foreach(opts.args, lambda job: 
            output(job.summary(**opts.kwargs)))

    def timeline(self, argv):
        opts = cmdline(argv, FLAGS_TIMELINE)
        self.foreach(opts.args, lambda job: 
            output(job.timeline(**opts.kwargs)))

    def touch(self, argv):
        self.foreach(argv, lambda job: job.touch())

    def unpause(self, argv):
        self.foreach(argv, lambda job: job.unpause())

def main():
    usage = "usage: %prog [options] <command> [<args>]"

    argv = sys.argv[1:]

    # Locate the command
    index = next((i for i, v in enumerate(argv) if not v.startswith('-')), -1)

    if index == -1: # No command
        options = argv
        command = ["list"]
    else:
        options = argv[:index]
        command = argv[index:]

    opts = parse(options, {}, ".splunkrc", usage=usage, epilog=HELP_EPILOG)
    service = connect(**opts.kwargs)
    program = Program(service)
    program.run(command)

if __name__ == "__main__":
    main()

