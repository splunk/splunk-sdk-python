"""The **splunklib.results** module provides a streaming XML reader for Splunk
search results.

Splunk search results can be returned in a variety of formats including XML,
JSON, and CSV. To make it easier to stream search results in XML format, they
are returned as a stream of XML *fragments*, not as a single XML document. This
module supports incrementally reading one result record at a time from such a
result stream. This module also provides a friendly iterator-based interface for
accessing search results while avoiding buffering the result set, which can be
very large.

To use the reader, instantiate :class:`JSONResultsReader` on a search result stream
as follows:::

    reader = ResultsReader(result_stream)
    for item in reader:
        print(item)
    print(f"Results are a preview: {reader.is_preview}")
"""

from .Message import Message
from .JSONResultsReader import JSONResultsReader
