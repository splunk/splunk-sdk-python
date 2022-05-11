import io
import gzip
import sys

from os import path

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
    data = io.TextIOWrapper(data)
    cmd = build_test_command()
    cmd._process_protocol_v2(sys.argv, data, sys.stdout)


def test_v1_searchcommand():
    data = gzip.open(get_input_file("v1_search_input"))
    data = io.TextIOWrapper(data)
    cmd = build_test_command()
    cmd._process_protocol_v1(["test_script.py", "__EXECUTE__"], data, sys.stdout)
