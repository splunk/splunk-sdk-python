import io

from splunklib.searchcommands import StreamingCommand, Configuration
from . import chunked_data_stream as chunky


def test_simple_streaming_command():
    @Configuration()
    class TestStreamingCommand(StreamingCommand):

        def stream(self, records):
            for record in records:
                record["out_index"] = record["in_index"]
                yield record

    cmd = TestStreamingCommand()
    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    data = []
    for i in range(0, 10):
        data.append({"in_index": str(i)})
    ifile.write(chunky.build_data_chunk(data, finished=True))
    ifile.seek(0)
    ofile = io.BytesIO()
    cmd._process_protocol_v2([], ifile, ofile)
    ofile.seek(0)
    output = chunky.ChunkedDataStream(ofile)
    getinfo_response = output.read_chunk()
    assert getinfo_response.meta["type"] == "streaming"


def test_field_preservation_negative():
    @Configuration()
    class TestStreamingCommand(StreamingCommand):

        def stream(self, records):
            for index, record in enumerate(records):
                if index % 2 != 0:
                    record["odd_field"] = True
                else:
                    record["even_field"] = True
                yield record

    cmd = TestStreamingCommand()
    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    data = []
    for i in range(0, 10):
        data.append({"in_index": str(i)})
    ifile.write(chunky.build_data_chunk(data, finished=True))
    ifile.seek(0)
    ofile = io.BytesIO()
    cmd._process_protocol_v2([], ifile, ofile)
    ofile.seek(0)
    output_iter = chunky.ChunkedDataStream(ofile).__iter__()
    next(output_iter)
    output_records = list(next(output_iter).data)

    # Assert that count of records having "odd_field" is 0
    assert len(list(r for r in output_records if "odd_field" in r)) == 0

    # Assert that count of records having "even_field" is 10
    assert len(list(r for r in output_records if "even_field" in r)) == 10


def test_field_preservation_positive():
    @Configuration()
    class TestStreamingCommand(StreamingCommand):

        def stream(self, records):
            for index, record in enumerate(records):
                if index % 2 != 0:
                    self.add_field(record, "odd_field", True)
                else:
                    self.add_field(record, "even_field", True)
                yield record

    cmd = TestStreamingCommand()
    ifile = io.BytesIO()
    ifile.write(chunky.build_getinfo_chunk())
    data = []
    for i in range(0, 10):
        data.append({"in_index": str(i)})
    ifile.write(chunky.build_data_chunk(data, finished=True))
    ifile.seek(0)
    ofile = io.BytesIO()
    cmd._process_protocol_v2([], ifile, ofile)
    ofile.seek(0)
    output_iter = chunky.ChunkedDataStream(ofile).__iter__()
    next(output_iter)
    output_records = list(next(output_iter).data)

    # Assert that count of records having "odd_field" is 10
    assert len(list(r for r in output_records if "odd_field" in r)) == 10

    # Assert that count of records having "even_field" is 10
    assert len(list(r for r in output_records if "even_field" in r)) == 10
