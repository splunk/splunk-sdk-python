import io

from splunklib import searchcommands
from . import chunked_data_stream as chunky


def test_simple_reporting_command():
    @searchcommands.Configuration()
    class TestReportingCommand(searchcommands.ReportingCommand):
        def reduce(self, records):
            value = 0
            for record in records:
                value += int(record["value"])
            yield {'sum': value}

    cmd = TestReportingCommand()
    ifile = io.BytesIO()
    data = []
    for i in range(0, 10):
        data.append({"value": str(i)})
    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_data_chunk(data))
    ifile.seek(0)
    ofile = io.BytesIO()
    cmd._process_protocol_v2([], ifile, ofile)
    ofile.seek(0)
    chunk_stream = chunky.ChunkedDataStream(ofile)
    getinfo_response = chunk_stream.read_chunk()
    assert getinfo_response.meta['type'] == 'reporting'
    data_chunk = chunk_stream.read_chunk()
    assert data_chunk.meta['finished'] is True  # Should only be one row
    data = list(data_chunk.data)
    assert len(data) == 1
    assert int(data[0]['sum']) == sum(range(0, 10))
