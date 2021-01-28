import io

from . import chunked_data_stream as chunky
from splunklib.searchcommands import StreamingCommand, Configuration


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
    data = list()
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
