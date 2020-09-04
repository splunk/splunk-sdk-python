import io
import gzip
import sys

from os import path

from splunklib import six
from splunklib.searchcommands import StreamingCommand, Configuration

def build_test_command():
    @Configuration()
    class TestSearchCommand(StreamingCommand):
        def stream(self, records):
            for record in records:
                yield record
    return TestSearchCommand()

def get_input_file(name):
    return path.join(
        path.dirname(path.dirname(__file__)), 'data', 'custom_search', name + '.gz')

def test_multibyte_chunked():
    data = gzip.open(get_input_file("multibyte_input"))
    if not six.PY2:
        data = io.TextIOWrapper(data)
    cmd = build_test_command()
    cmd._process_protocol_v2(sys.argv, data, sys.stdout)
