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
        pprint(item)
"""

from cStringIO import StringIO
import xml.dom.pulldom as pulldom

__all__ = [
    "ResultsReader"
]

# Splices a list of strings and file-like objects into a single stream
class ListStream(object):
    def __init__(self, *args):
        count = len(args)
        if count == 0:
            self.args = []
            self.file = None
        else:
            self.args = args
            self.file = self._next()

    def read(self, size):
        result = ""
        while True:
            if self.file is None: 
                return result
            chunk = self.file.read(size)
            result += chunk
            count = len(chunk)
            if count == size: 
                return result
            size -= count
            self.file = self._next()

    def _next(self):
        if len(self.args) == 0: 
            return None
        item = self.args[0]
        self.args = self.args[1:]
        if isinstance(item, str): 
            return StringIO(item)
        return item
            
# A file-like interface that will convert a stream of XML fragments, into
# a well-formed XML document by injecting a root element into the stream.
# This is basically an annoying hack and I'd love a better idea.
class XMLStream(object):
    def __init__(self, file_):
        self.file = XMLStream.prepare(file_)

    # Prepare the stream by scanning the head of the stream until we find 
    # the first XML element so that we know where to inject the artificial 
    # document wrapper.
    @staticmethod
    def prepare(file_):
        head = ""
        start = 0
        headsize = 0
        while True:
            chunk = file_.read(180)
            chunksize = len(chunk)
            if chunksize == 0: 
                return
            head += chunk
            headsize += chunksize
            index = head.find('<', start)
            if index == -1: # Not found
                start = headsize
                continue
            if index+1 == headsize: # Found on last byte of head
                # Comment or PI char may the first char in the in next 
                # chunk .. so advance start pointer to current index and 
                # read next chunk
                start = index
                continue
            next_ = head[index+1]
            if next_ == '!' or next_ == '?':
                start = index+1
                continue
            # Splice the doc wrapper elements in to place
            return ListStream(
                head[:index], "<doc>", head[index:], file_, "</doc>\n")

    def read(self, size):
        if self.file is not None:
            return self.file.read(size)
        else:
            raise StopIteration
            
# A simplified XML 'reader' interface, that also abstracts the pulldom
TAG = "TAG"         # kind, name, attrs
END = "END"         # kind, name
VAL = "VAL"         # kind, value
class XMLReader(object):
    def __init__(self, stream):
        self._items = pulldom.parse(XMLStream(stream), bufsize = 256)
        self._item = None   # The current item
        self._next = None   # 1 item pushback buffer
        self.kind = None
        self.name = None
        self.attrs = None
        self.value = None

    def __iter__(self):
        return self

    def _scan(self):
        if self._next is not None:
            item = self._next
            self._next = None
            return item
        try:
            item = self._items.next()
        except StopIteration:
            item = None
        return item

    def _push(self, item):
        assert self._next is None
        self._next = item

    def expand(self):
        """Expands the current node into a minidom."""
        if not self.kind == TAG: 
            raise Exception, "Illegal operation"
        node = self._item[1]
        self._items.expandNode(node)
        return node

    @property
    def item(self):
        return {
            TAG: (TAG, self.name, self.attrs),
            END: (END, self.name),
            VAL: (VAL, self.value)
        }[self.kind]

    def isend(self, name = None):
        if self.kind != END: 
            return False
        if name is not None: 
            return name == self.name
        return True

    def istag(self, name = None):
        if self.kind != TAG: 
            return False
        if name is not None: 
            return name == self.name
        return True

    def isval(self):
        return self.kind == VAL

    def next(self):
        """An iterator interface to the reader that returns a tuple of values
           that correspond to the current item."""
        if self.read() is None: 
            raise StopIteration
        return self.item

    def read(self):
        self._item = self._scan()

        if self._item is None: 
            self.kind = None
            self.name = None
            self.attrs = None
            self.value = None
            return None

        elem, name = self._item

        if elem == pulldom.START_ELEMENT:
            self.kind = TAG
            self.name = name.tagName
            self.attrs = dict(name.attributes.items()) \
                if name.hasAttributes() else None
            self.value = None
            return TAG

        if elem == pulldom.END_ELEMENT:
            self.kind = END
            self.name = name.tagName
            self.attrs = None
            self.value = None
            return END

        if elem == pulldom.CHARACTERS:
            self.kind = VAL
            self.name = None
            self.attrs = None
            self.value = name.data
            while True: # Merge adjacent CHARACTERS
                elem, name = item = self._scan()
                if elem != pulldom.CHARACTERS:
                    self._push(item)
                    break
                self.value += name.data
            if len(self.value.strip()) == 0: 
                self.read()
            return VAL

        if elem == pulldom.START_DOCUMENT: # Ignore
            return self.read() 

        if elem == pulldom.END_DOCUMENT:
            return None # done

        assert False # Unexpected

MESSAGE = "MESSAGE"
RESULT = "RESULT"
RESULTS = "RESULTS"
class ResultsReader(object):
    """A class that provides a forward-only, streaming search results reader."""
    def __init__(self, stream):
        self._reader = XMLReader(stream)
        self.kind = None
        self.value = None
        self.fields = None

    def __iter__(self):
        return self

    def _checktag(self, name = None):
        if not self._istag(name): 
            self._error() 

    def _checkend(self, name = None):
        if not self._isend(name): 
            self._error()
    
    def _checkval(self):
        if (not self._isval() and not self._isend()): 
            self._error()

    def _error(self):
        raise Exception, "Unexpected item: %s" % repr(self._reader.item)

    def _istag(self, name = None):
        return self._reader.istag(name)

    def _isend(self, name = None):
        return self._reader.isend(name)

    def _isval(self):
        return self._reader.isval()

    def _read_message(self):
        type_ = self._reader.attrs["type"]
        message = self._scanval()
        self._scanend("msg")
        self.kind = MESSAGE
        self.value = {'type': type_, 'message': message }
        return MESSAGE

    def _read_meta(self):
        self._scantag("fieldOrder")
        while True:
            self._scan()
            if self._isend("fieldOrder"): 
                break
            self._checktag("field")
            value = self._scanval()
            self.fields.append(value)
            self._scanend("field")
        self._scanend("meta")

    # Reads a single search result record.
    def _read_result(self):
        result = {}
        offset = self._reader.attrs['offset'].encode("utf8")
        while True:
            self._scan()

            if self._isend("result"): 
                break

            self._checktag("field")
            key = self._reader.attrs["k"].encode("utf8")
            name = self._scantag()

            if name == "v":
                result[key] = self._reader.expand().toxml("utf8")
                self._scanend("field")
            elif name == "value":
                result[key] = self._read_value()
                self._checkend("field")
            else: self._error()

        self.kind = RESULT
        result['$offset'] = offset
        self.value = result
        return RESULT

    # Reads the results section header and metadata
    def _read_results(self):
        self.fields = []
        self.kind = RESULTS
        self.value = self._reader.attrs
        self._scantag("meta")
        self._read_meta()
        return RESULTS

    # Reads a field value, handle single and multi-valied fields.
    def _read_value(self):
        value = []
        while True:
            self._checktag("value")
            self._scantag("text")
            val = self._scanval()

            if val:
                value.append(val.encode("utf8"))
                self._scanend("text")
            else:
                value.append("")
                
            self._scanend("value")
            self._scan()
            if self._isend("field"): 
                break
        return value[0] if len(value) == 1 else value

    def _scan(self):
        self._reader.read()
        return self._reader.kind

    def _scantag(self, name = None):
        self._reader.read()
        self._checktag(name)
        return self._reader.name

    def _scanend(self, name = None):
        self._reader.read()
        self._checkend(name)
        return self._reader.name

    def _scanval(self):
        self._reader.read()
        self._checkval()
        return self._reader.value

    @property
    def item(self):
        return (self.kind, self.value)

    def next(self):
        kind = self.read()
        if kind is None or self.value is None: 
            raise StopIteration()
        return self.item

    # Read the next search result, handling new sections and section metadata 
    # as necessarry. NOTE: if the pulldom reader raises StopIteration, we 
    # simply pass that through to indicate the end of our iterable.
    def read(self):
        while True:
            kind = self._scan()

            if kind == TAG:
                name = self._reader.name
                if name == "result":
                    return self._read_result()
                if name == "msg":
                    return self._read_message()
                if name == "results":
                    return self._read_results()
                if name == "messages":
                    continue # Ignore the 'messages' wrapper, we dont validate
                if name == "doc":
                    continue # Skip synthetic root element

            if kind == END:
                name = self._reader.name
                if name == "results":
                    continue
                if name == "messages":
                    continue # Keep looking for results
                if name == "doc":
                    continue # Skip synthetic root end-element

            if kind is None: 
                return None

            self._error()

