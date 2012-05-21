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

"""This module provides a streaming XML reader for Splunk search results.

Splunk search results can be returned in a variety of formats including XML,
JSON, and CSV. Search results in XML format are returned as a stream of XML 
*fragments*, not as a single XML document, to make it easier to stream search 
results. This module supports incrementally reading one result record at a time 
from such a result stream. This module also provides a friendly iterator-based 
interface for accessing search results while avoiding buffering of the result 
set, which can be very large.

To use the reader, instantiate **ResultsReader** on a search result stream::

    reader = ResultsReader(result_stream)
    for item in reader:
        print(item)
    print "Results are a preview: %s" % reader.is_preview
"""

try:
    import xml.etree.cElementTree as et
except:
    import xml.etree.ElementTree as et

from collections import OrderedDict

__all__ = [
    "ResultsReader",
    "Message"
]

class Message(object):
    def __init__(self, type_, message):
        self.type = type_
        self.message = message
    def __repr__(self):
        print "%s: %s" % (type, message)

class ResultsReader(object):
    """Lazily yield dicts from a streaming XML results stream.

    ``ResultsReader`` is iterable. What comes back are either
    ``dict``s (for results) or ``Message`` objects (for Splunk
    messages). It has one field: ``is_preview``, which is ``True`` if
    the results returned are a preview from a running search, or
    ``False`` if the results come from a completed search. For example,::

    :param stream: The stream to read from (any object support ``.read()``).

    This function has no network activity other than what is implicit
    in the stream it operates on.

    **Example**:

    import results
    response = ... # the body of an HTTP response
    reader = results.ResultsReader(response)
    for result in reader:
        if isinstance(result, dict):
            print "Result: %s" % result
        elif isinstance(result, results.Message):
            print "Message: %s" % result
    print "is_preview = %s " % reader.is_preview)
    """
    # Be sure to update the docstrings of client.Jobs.oneshot,
    # client.Job.results_preview and client.Job.results to match any
    # changes made to ResultsReader.
    #
    # This wouldn't be a class, just the parse_results function below,
    # except that you cannot get the current generator inside the
    # function creating that generator. Thus it's all wrapped up for
    # the sake of one field.
    def __init__(self, stream):
            self._gen = self.parse_results(stream)
            # splunkd 4.3 returns an empty response body instead of a
            # results element with no result elements inside. There is
            # no good way to handle it other than failing out and
            # trying to get to a sane state.
            try:
                self.is_preview = self._gen.next()
            except StopIteration:
                self.is_preview = None

    def __iter__(self):
        return self

    def next(self):
        return self._gen.next()

    def parse_results(self, stream):
        result = None
        values = None
        try:
            for event, elem in et.iterparse(stream, events=('start', 'end')):
                if elem.tag == 'results' and event == 'start':
                    # The wrapper element is a <results preview="0|1">. We
                    # don't care about it except to tell is whether these
                    # are preview results, or the final results from the
                    # search.
                    is_preview = elem.attrib['preview'] == '1'
                    yield is_preview
                if elem.tag == 'result':
                    if event == 'start':
                        result = OrderedDict()
                    elif event == 'end':
                        yield result
                        result = None
                        elem.clear()
    
                elif elem.tag == 'field' and result is not None:
                    # We need the 'result is not None' check because
                    # 'field' is also the element name in the <meta>
                    # header that gives field order, which is not what we
                    # want at all.
                    if event == 'start':
                        values = []
                    elif event == 'end':
                        field_name = elem.attrib['k'].encode('utf8')
                        if len(values) == 1:
                            result[field_name] = values[0]
                        else:
                            result[field_name] = values
                        # Calling .clear() is necessary to let the
                        # element be garbage collected. Otherwise
                        # arbitrarily large results sets will use
                        # arbitrarily large memory intead of
                        # streaming.
                        elem.clear()
    
                elif elem.tag == 'text' and event == 'end':
                    values.append(elem.text.encode('utf8'))
                    elem.clear()
    
                elif elem.tag == 'msg':
                    if event == 'start':
                        msg_type = elem.attribs['type']
                    elif event == 'end':
                        yield Message(msg_type, elem.text.encode('utf8'))
                        elem.clear()
        except et.ParseError as pe:
            # This is here to handle the same incorrect return from
            # splunk that is described in __init__.
            if 'no element found' in pe.msg:
                return
            else:
                raise



