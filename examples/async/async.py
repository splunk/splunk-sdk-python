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

# A sample that demonstrates a custom HTTP handler for the Splunk service,
# as well as showing how you could use the Splunk SDK for Python with coroutine
# based systems like Eventlet.

#### Main Code

import sys, os, datetime
import urllib
import ssl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import splunklib.binding as binding
import splunklib.client as client
try:
    from utils import parse, error
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


# Placeholder for a specific implementation of `urllib2`,
# to be defined depending on whether or not we are running
# this sample in async or sync mode.
urllib2 = None

def _spliturl(url):
    scheme, part = url.split(':', 1)
    host, path = urllib.splithost(part)
    host, port = urllib.splitnport(host, 80)
    return scheme, host, port, path

def main(argv):
    global urllib2
    usage = "async.py <sync | async>"

    # Parse the command line args.
    opts = parse(argv, {}, ".splunkrc")

    # We have to see if we got either the "sync" or
    # "async" command line arguments.
    allowed_args = ["sync", "async"]
    if len(opts.args) == 0 or opts.args[0] not in allowed_args:
        error("Must supply either of: %s" % allowed_args, 2)

    # Note whether or not we are async.
    is_async = opts.args[0] == "async"

    # If we're async, we'' import `eventlet` and `eventlet`'s version
    # of `urllib2`. Otherwise, import the stdlib version of `urllib2`.
    #
    # The reason for the funky import syntax is that Python imports
    # are scoped to functions, and we need to make it global. 
    # In a real application, you would only import one of these.
    if is_async:
        urllib2 = __import__('eventlet.green', globals(), locals(), 
                            ['urllib2'], -1).urllib2
    else:
        urllib2 = __import__("urllib2", globals(), locals(), [], -1)


    # Create the service instance using our custom HTTP request handler.
    service = client.Service(handler=request, **opts.kwargs)
    service.login()

    # Record the current time at the start of the
    # "benchmark".
    oldtime = datetime.datetime.now()

    def do_search(query):
        # Create a search job for the query.

        # In the async case, eventlet will "relinquish" the coroutine
        # worker, and let others go through. In the sync case, we will
        # block the entire thread waiting for the request to complete.
        job = service.jobs.create(query, exec_mode="blocking")

        # We fetch the results, and cancel the job
        results = job.results()
        job.cancel()

        return results

    # We specify many queries to get show the advantages
    # of paralleism.
    queries = [
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
        'search * | head 100',
    ]

    # Check if we are async or not, and execute all the
    # specified queries.
    if is_async:
        import eventlet

        # Create an `eventlet` pool of workers.
        pool = eventlet.GreenPool(16)

        # If we are async, we use our worker pool to farm
        # out all the queries. We just pass, as we don't
        # actually care about the result.
        for results in pool.imap(do_search, queries):
            pass
    else:
        # If we are sync, then we just execute the queries one by one,
        # and we can also ignore the result.
        for query in queries:
            do_search(query)
    
    # Record the current time at the end of the benchmark,
    # and print the delta elapsed time.
    newtime = datetime.datetime.now()
    print "Elapsed Time: %s" % (newtime - oldtime)
    

##### Custom `urllib2`-based HTTP handler

def request(url, message, **kwargs):
    # Split the URL into constituent components.
    scheme, host, port, path = _spliturl(url)
    body = message.get("body", "")

    # Setup the default headers.
    head = { 
        "Content-Length": str(len(body)),
        "Host": host,
        "User-Agent": "http.py/1.0",
        "Accept": "*/*",
    }

    # Add in the passed in headers.
    for key, value in message["headers"]: 
        head[key] = value

    # Note the HTTP method we're using, defaulting
    # to `GET`.
    method = message.get("method", "GET")
    
    # Note that we do not support proxies in this example
    # If running Python 2.7.9+, disable SSL certificate validation
    if sys.version_info >= (2, 7, 9):
        unverified_ssl_handler = urllib2.HTTPSHandler(context=ssl._create_unverified_context())
        opener = urllib2.build_opener(unverified_ssl_handler)
    else:
        opener = urllib2.build_opener()

    # Unfortunately, we need to use the hack of 
    # "overriding" `request.get_method` to specify
    # a method other than `GET` or `POST`.
    request = urllib2.Request(url, body, head)
    request.get_method = lambda: method

    # Make the request and get the response
    response = None
    try:
        response = opener.open(request)
    except Exception as e:
        response = e

    # Normalize the response to something the SDK expects, and 
    # return it.
    return {
        'status': response.code, 
        'reason': response.msg,
        'headers': response.info().dict,
        'body': binding.ResponseReader(response)
    }

if __name__ == "__main__":
    main(sys.argv[1:])

