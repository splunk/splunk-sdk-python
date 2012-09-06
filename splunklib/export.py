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
Exporting large amounts of data from Splunk indexes.

Exporting is meant to be robust in the presence of program failures. So when
lightning strikes your data center and the script that's been running for a
day and a half dies, you should be able to restart it and have it resume
pulling data from Splunk at the event where it left off.

There is a corner case, though: the export may have yielded an event but the
program died before that event could be written, or, worse, you may have
buffered N events, none of which were yet written when the program died. We
provide a reyield_last method where appropriate to let you fetch the previous
events if there were any and rewrite them. It defaults to reyielding the last
1 event, but you can set it to 0 or to any other fixed number.
"""

import os
import copy

class MalformedRestartFile(Exception):
    pass

def downsample(span):
    if span > 86400:
        return 86400
    elif span > 3600:
        return 3600
    elif span > 60:
        return 60
    else:
        return 1

class Bucket(object):
    def __init__(self):
        raise SyntaxError("Cannot instantiate Bucket.")

class FreshBucket(Bucket):
    def __init__(self, index_name, earliest_time, latest_time):
        if earliest_time >= latest_time:
            raise ValueError("earliest_time must be strictly after latest_time")
        self.index_name = index_name
        self.earliest_time = earliest_time
        self.latest_time = latest_time

    def events(self, search_fun):
        events = search_fun(
            index_name=self.index_name,
            earliest_time=self.earliest_time,
            latest_time=self.latest_time,
            offset=0
        )
        for event in events:
            yield event

    def __str__(self):
        return 'FreshBucket(index_name=%s, earliest_time=%s, latest_time=%s)' % \
               (str(self.index_name), str(self.earliest_time), str(self.latest_time))

    def __repr__(self):
        return str(self)

    def refine(self, timeline_func, min_span=1, event_limit=1e4):
        current_span = self.latest_time - self.earliest_time
        [d] = timeline_func(self.index_name, self.earliest_time, self.latest_time, current_span)
        n_events = d['n_events']
        if current_span <= min_span or n_events <= event_limit:
            return [self]
        else:
            new_span = downsample(current_span)
            timeline = timeline_func(self.index_name, self.earliest_time, self.latest_time, new_span)
            all_buckets = []
            for section in timeline:
                new_bucket = FreshBucket(
                    index_name=self.index_name,
                    earliest_time=section['earliest_time'],
                    latest_time=section['earliest_time'] + section['span'],
                )
                if section['n_events'] <= event_limit:
                    all_buckets.append(new_bucket)
                else:
                    all_buckets.extend(new_bucket.refine(timeline_func, min_span, event_limit))
            return all_buckets

    def __eq__(self, other):
        return isinstance(other, FreshBucket) and \
            self.index_name == other.index_name and \
            self.earliest_time == other.earliest_time and \
            self.latest_time == other.latest_time

class PartialBucket(Bucket):
    def __init__(self, index_name, earliest_time, latest_time, offset):
        if earliest_time >= latest_time:
            raise ValueError("earliest_time must be strictly after latest_time")
        self.index_name = index_name
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.offset = offset

    def __str__(self):
        return 'PartialBucket(index_name=%s, earliest_time=%s, latest_time=%s, offset=%s)' %\
               (str(self.index_name), str(self.earliest_time), str(self.latest_time), repr(self.offset))

    def __repr__(self):
        return str(self)

    def events(self, search_fun):
        events = search_fun(
            index_name=self.index_name,
            earliest_time=self.earliest_time,
            latest_time=self.latest_time,
            offset=self.offset
        )
        for event in events:
            yield event

    def __eq__(self, other):
        return isinstance(other, PartialBucket) and \
            self.index_name == other.index_name and \
            self.earliest_time == other.earliest_time and \
            self.latest_time == other.latest_time and \
            self.offset == other.offset

class FinishedBucket(Bucket):
    def __init__(self, index_name, earliest_time, latest_time, n_events):
        if earliest_time >= latest_time:
            raise ValueError("earliest_time must be strictly after latest_time")
        self.index_name = index_name
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.n_events = n_events

    def __str__(self):
        return 'FinishedBucket(index_name=%s, earliest_time=%s, latest_time=%s, n_events=%s)' %\
            (str(self.index_name), str(self.earliest_time), str(self.latest_time), str(self.n_events))

    def __repr__(self):
        return str(self)


    def events(self, search_fun):
        # yield in the function body causes this function to be compiled into
        # a generator, but it will immediately raise StopIteration.
        if False:
            yield None

    def __eq__(self, other):
        return isinstance(other, FinishedBucket) and \
            self.index_name == other.index_name and \
            self.earliest_time == other.earliest_time and \
            self.latest_time == other.latest_time

class IndexExporter(object):
    def __init__(self, index_name, earliest_time, latest_time, search_func, timeline_func,
                 min_span=1, event_limit=1e4, restart=True, rewind=0):
        self.index_name = index_name
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.search_func = search_func
        self.timeline_func = timeline_func
        self.min_span = min_span
        self.event_limit = event_limit
        self.restart = restart
        self.rewind = rewind

        if isinstance(restart, basestring):
            restart_path = restart
        else:
            restart_path = default_restart_path(index_name, earliest_time, latest_time)

        if os.path.exists(restart_path) and restart:
            self.restart_file = RestartFile(restart_path, rewind=rewind)
            plan = self.restart_file.plan
        else:
            plan = FreshBucket(
                index_name=index_name,
                earliest_time=earliest_time,
                latest_time=latest_time,
            ).refine(timeline_func, min_span, event_limit)
            self.restart_file = RestartFile(restart_path, plan=plan)

        self.bucket_index = 0
        self.event_offset = 1

        self.n_rewound = self.restart_file.n_rewound
        self.bucket_gen = iter(plan)
        self.event_gen = self.bucket_gen.next().events(search_func)

    def __iter__(self):
        return self

    def next(self):
        while True:
            try:
                event = self.event_gen.next()
                self.restart_file.log(self.bucket_index, self.event_offset)
                self.event_offset += 1
                return event
            except StopIteration:
                bucket = self.bucket_gen.next()
                self.bucket_index += 1
                self.event_gen = bucket.events(self.search_func)

def default_restart_path(index_name, earliest_time, latest_time):
    basedir = os.getcwd()
    filename = '%s-%d-%d.rst' % (index_name, earliest_time, latest_time)
    return os.path.join(basedir, filename)

def read_null_terminated_ascii_string(handle, maxlen=256):
    s = ''
    while len(s) <= maxlen:
        c = handle.read(1)
        if c == '':
            raise ValueError("Reached EOF before null termination of string (found: %s)", s)
        elif c == '\0':
            return s
        else:
            s += c
    raise ValueError('String was longer than maximum length to read of %d (read so far: %s)' % (maxlen, s))

def write_null_terminated_ascii_string(handle, s, maxlen=256):
    if '\0' in s:
        raise ValueError("Cannot write string containing null characters.")
    if len(s) > maxlen:
        raise ValueError("Will not write a string with length greater than maxlen (here: %d)" % maxlen)
    handle.write(s)
    handle.write('\0')

def read_int64(handle):
    v = 0
    for i in range(8):
        c = handle.read(1)
        if c == '':
            raise ValueError("Unexpected EOF while reading 64 bit integer.")
        v += ord(c) << (8*(7-i))
    return v

def write_int64(handle, val):
    for i in range(8):
        q = (val >> (8*(7-i))) % 256
        handle.write(chr(q))

def read_plan(handle):
    index_name = read_null_terminated_ascii_string(handle)
    buckets = []
    while True:
        earliest_time, latest_time = read_int64(handle), read_int64(handle)
        if (earliest_time, latest_time) == (0, 0):
            break
        else:
            bucket = FreshBucket(
                index_name=index_name,
                earliest_time=earliest_time,
                latest_time=latest_time
            )
            buckets.append(bucket)

    return buckets

def write_plan(handle, buckets):
    if len(buckets) == 0:
        return
    index_name = buckets[0].index_name
    write_null_terminated_ascii_string(handle, index_name)
    for bucket in buckets:
        if not isinstance(bucket, FreshBucket):
            raise ValueError("Cannot write Partial or Finished buckets in plans.")
        else:
            write_int64(handle, bucket.earliest_time)
            write_int64(handle, bucket.latest_time)
    write_int64(handle, 0)
    write_int64(handle, 0)
    handle.flush()

def read_log(handle):
    log = []
    while True:
        try:
            bucket_idx = read_int64(handle)
        except ValueError:
            return log # This just means we have run out of log to read.

        if log != [] and bucket_idx <= log[-1]['bucket']:
            raise MalformedRestartFile('Log entry %d did not have a higher index than the previous entry.' % len(log))

        try:
            offset = read_int64(handle)
        except ValueError:
            raise MalformedRestartFile("Log record %d is malformed in file." % len(log))
        log.append({'bucket': bucket_idx, 'offset': offset})

def write_log_entry(handle, bucket_index, offset):
    handle.seek(0, 2)
    write_int64(handle, bucket_index)
    write_int64(handle, offset)

def update_log_entry(handle, new_offset):
    assert handle.mode == 'r+b' # Otherwise overwriting doesn't work properly
    handle.seek(-8, 2) # Step back by one int64
    write_int64(handle, new_offset)

def update_plan_with_log(plan, log):
    # Assume log is sane. Therefore all buckets in plan are finished except the last one mentioned in log.
    if len(log) == 0:
        return plan
    else:
        bucket_index = log[-1]['bucket']
        offset = log[-1]['offset']
        assert bucket_index >= 0
        assert offset >= 0
        assert bucket_index < len(plan)
        new_plan = []
        # Everything up to the last bucket in the log is finished.
        for bucket in plan[:bucket_index]:
            new_plan.append(FinishedBucket(
                index_name=bucket.index_name,
                earliest_time=bucket.earliest_time,
                latest_time=bucket.latest_time,
                n_events=0
            ))
        for entry in log[:-1]:
            new_plan[entry['bucket']].n_events = entry['offset']
        # Add the last logged bucket.
        bucket = plan[bucket_index]
        if offset == 0:
            new_plan.append(FreshBucket(
                index_name=bucket.index_name,
                earliest_time=bucket.earliest_time,
                latest_time=bucket.latest_time
            ))
        else:
            new_plan.append(PartialBucket(
                index_name=bucket.index_name,
                earliest_time=bucket.earliest_time,
                latest_time=bucket.latest_time,
                offset=offset
            ))
        # Add the rest of the buckets
        new_plan.extend(plan[bucket_index+1:])
    return new_plan

def rewind_plan(plan, n):
    original_n = n
    new_plan = copy.copy(plan)
    i = len(new_plan)-1
    while n > 0 and i >= 0:
        old_bucket = plan[i]
        if isinstance(old_bucket, FreshBucket):
            i -= 1
        elif isinstance(old_bucket, PartialBucket):
            if old_bucket.offset <= n:
                new_plan[i] = FreshBucket(
                    index_name=old_bucket.index_name,
                    earliest_time=old_bucket.earliest_time,
                    latest_time=old_bucket.latest_time
                )
                n -= old_bucket.offset
                i -= 1
            elif old_bucket.offset > n:
                new_plan[i] = PartialBucket(
                    index_name=old_bucket.index_name,
                    earliest_time=old_bucket.earliest_time,
                    latest_time=old_bucket.latest_time,
                    offset=old_bucket.offset - n
                )
                n = 0
        elif isinstance(old_bucket, FinishedBucket):
            if old_bucket.n_events <= n:
                new_plan[i] = FreshBucket(
                    index_name=old_bucket.index_name,
                    earliest_time=old_bucket.earliest_time,
                    latest_time=old_bucket.latest_time
                )
                n -= old_bucket.n_events
                i -= 1
            elif old_bucket.n_events > n:
                new_plan[i] = PartialBucket(
                    index_name=old_bucket.index_name,
                    earliest_time=old_bucket.earliest_time,
                    latest_time=old_bucket.latest_time,
                    offset=old_bucket.n_events - n
                )
                n = 0
        else:
            raise ValueError('Invalid Bucket type: %s' % str(old_bucket))
    n_rewound = original_n-n
    return (n_rewound, new_plan)

class RestartFile(object):
    def __init__(self, path, plan=None, rewind=0, overwrite=False):
        self.path = path
        if not os.path.exists(path) or overwrite:
            self.is_restarted = False
            if plan is None:
                raise ValueError('Must provide a plan when creating a new RestartFile.')
            open(path, 'wb').close() # Ensure file exists
            self.handle = open(path, 'r+b')
            self.plan = plan
            write_plan(self.handle, plan)
            self.handle.flush()
            self.handle.seek(0, 2) # Seek to end of file
            self.n_rewound = 0
        else:
            self.is_restarted = True
            if plan is not None:
                raise ValueError('Restart file %s already exists; please manually delete or specify overwrite.' % self.path)
            self.handle = open(self.path, 'r+b')
            plan = read_plan(self.handle)
            log = read_log(self.handle)
            updated_plan = update_plan_with_log(plan, log)
            self.n_rewound, self.plan = rewind_plan(updated_plan, rewind)
        self.last_bucket_index = -1

    def log(self, bucket_index, n):
        assert bucket_index >= self.last_bucket_index
        if self.last_bucket_index == bucket_index:
            update_log_entry(self.handle, n)
        else:
            write_log_entry(self.handle, bucket_index, n)
            self.last_bucket_index = bucket_index
        self.handle.flush()

    def close(self):
        self.handle.flush()
        self.handle.close()
