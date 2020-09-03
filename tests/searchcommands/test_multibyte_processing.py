from splunklib.searchcommands import StreamingCommand, Configuration, dispatch
import gzip
import os
import io
import sys


def build_test_command():
    @Configuration()
    class TestSearchCommand(StreamingCommand):
        def stream(self, records):
            for record in records:
                yield record
    return TestSearchCommand()


def get_input_file(name):
    return "tests/data/custom_search/" + name + ".gz"


def test_multibyte_chunked(capsys):
    data = gzip.open(get_input_file("multibyte_input"))
    if sys.version_info.major >= 3:
        data = io.TextIOWrapper(data)
    cmd = build_test_command()
    cmd._process_protocol_v2(sys.argv, data, sys.stdout)
