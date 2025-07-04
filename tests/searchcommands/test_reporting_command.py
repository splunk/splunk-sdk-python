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


def test_simple_reporting_command_with_map():
    @searchcommands.Configuration()
    class MapAndReduceReportingCommand(searchcommands.ReportingCommand):
        def map(self, records):
            for record in records:
                record["value"] = str(int(record["value"]) * 2)
                yield record

        def reduce(self, records):
            total = 0
            for record in records:
                total += int(record["value"])
            yield {"sum": total}

    cmd = MapAndReduceReportingCommand()
    ifile = io.BytesIO()

    input_data = [{"value": str(i)} for i in range(5)]

    mapped_data = list(cmd.map(input_data))

    ifile.write(chunky.build_getinfo_chunk())
    ifile.write(chunky.build_data_chunk(mapped_data))
    ifile.seek(0)

    ofile = io.BytesIO()
    cmd._process_protocol_v2([], ifile, ofile)

    ofile.seek(0)
    chunk_stream = chunky.ChunkedDataStream(ofile)
    chunk_stream.read_chunk()
    data_chunk = chunk_stream.read_chunk()
    assert data_chunk.meta['finished'] is True

    result = list(data_chunk.data)
    expected_sum = sum(i * 2 for i in range(5))
    assert int(result[0]["sum"]) == expected_sum
