import io
import time

from . import chunked_data_stream as chunky

from splunklib.searchcommands import Configuration, GeneratingCommand


def test_simple_generator():
    @Configuration()
    class GeneratorTest(GeneratingCommand):
        def generate(self):
            for num in range(1, 10):
                yield {'_time': time.time(), 'event_index': num}
    generator = GeneratorTest()
    in_stream = io.BytesIO()
    in_stream.write(chunky.build_getinfo_chunk())
    in_stream.write(chunky.build_chunk({'action': 'execute'}))
    in_stream.seek(0)
    out_stream = io.BytesIO()
    generator._process_protocol_v2([], in_stream, out_stream)
    out_stream.seek(0)

    ds = chunky.ChunkedDataStream(out_stream)
    is_first_chunk = True
    finished_seen = False
    expected = set(map(lambda i: str(i), range(1, 10)))
    seen = set()
    for chunk in ds:
        if is_first_chunk:
            assert chunk.meta["generating"] is True
            assert chunk.meta["type"] == "stateful"
            is_first_chunk = False
        finished_seen = chunk.meta.get("finished", False)
        for row in chunk.data:
            seen.add(row["event_index"])
    print(out_stream.getvalue())
    print(expected)
    print(seen)
    assert expected.issubset(seen)
    assert finished_seen



