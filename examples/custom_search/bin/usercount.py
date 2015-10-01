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

import csv, StringIO, sys, urllib

# Tees output to a logfile for debugging
class Logger:
    def __init__(self, filename, buf = None):
        self.log = open(filename, 'w')
        self.buf = buf

    def flush(self):
        self.log.flush()

        if self.buf is not None:
            self.buf.flush()

    def write(self, message):
        self.log.write(message)
        self.log.flush()
        
        if self.buf is not None:
            self.buf.write(message)
            self.buf.flush()

# Tees input as it is being read, also logging it to a file
class Reader:
    def __init__(self, buf, filename = None):
        self.buf = buf
        if filename is not None:
            self.log = open(filename, 'w')
        else:
            self.log = None

    def __iter__(self):
        return self

    def next(self):
        return self.readline()

    def readline(self):
        line = self.buf.readline()

        if not line:
            raise StopIteration

        # Log to a file if one is present
        if self.log is not None:
            self.log.write(line)
            self.log.flush()

        # Return to the caller
        return line

def output_results(results, mvdelim = '\n', output = sys.stdout):
    """Given a list of dictionaries, each representing
    a single result, and an optional list of fields,
    output those results to stdout for consumption by the
    Splunk pipeline"""

    # We collect all the unique field names, as well as 
    # convert all multivalue keys to the right form
    fields = set()
    for result in results:    
        for key in result.keys():
            if(isinstance(result[key], list)):
                result['__mv_' + key] = encode_mv(result[key])
                result[key] = mvdelim.join(result[key])
        fields.update(result.keys())

    # convert the fields into a list and create a CSV writer
    # to output to stdout
    fields = sorted(list(fields))

    writer = csv.DictWriter(output, fields)

    # Write out the fields, and then the actual results
    writer.writerow(dict(zip(fields, fields)))
    writer.writerows(results)

def read_input(buf, has_header = True):
    """Read the input from the given buffer (or stdin if no buffer)
    is supplied. An optional header may be present as well"""

    # Use stdin if there is no supplied buffer
    if buf is None:
        buf = sys.stdin

    # Attempt to read a header if necessary
    header = {}
    if has_header:
        # Until we get a blank line, read "attr:val" lines, 
        # setting the values in 'header'
        last_attr = None
        while True:
            line = buf.readline()

            # remove lastcharacter (which is a newline)
            line = line[:-1] 

            # When we encounter a newline, we are done with the header
            if len(line) == 0:
                break

            colon = line.find(':')

            # If we can't find a colon, then it might be that we are
            # on a new line, and it belongs to the previous attribute
            if colon < 0:
                if last_attr:
                    header[last_attr] = header[last_attr] + '\n' + urllib.unquote(line)
                else:
                    continue

            # extract it and set value in settings
            last_attr = attr = line[:colon]
            val  = urllib.unquote(line[colon+1:])
            header[attr] = val

    return buf, header

def encode_mv(vals):
    """For multivalues, values are wrapped in '$' and separated using ';'
    Literal '$' values are represented with '$$'"""
    s = ""
    for val in vals:
        val = val.replace('$', '$$')
        if len(s) > 0:
            s += ';'
        s += '$' + val + '$'

    return s

def main(argv):
    stdin_wrapper = Reader(sys.stdin)
    buf, settings = read_input(stdin_wrapper, has_header = True)
    events = csv.DictReader(buf)
    
    results = []

    for event in events:
        # For each event, we read in the raw event data
        raw = StringIO.StringIO(event["_raw"])
        top_output = csv.DictReader(raw, delimiter = ' ', skipinitialspace = True)
    
        # And then, for each row of the output of the 'top' command
        # (where each row represents a single process), we look at the
        # owning user of that process.
        usercounts = {}
        for row in top_output:
            user = row["USER"]
            user = user if not user.startswith('_') else user[1:]
    
            usercount = 0
            if usercounts.has_key(user):
                usercount = usercounts[user]
    
            usercount += 1
            usercounts[user] = usercount
    
        results.append(usercounts)
    
    # And output it to the next stage of the pipeline
    output_results(results)


if __name__ == "__main__":
    try: 
        main(sys.argv)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)
