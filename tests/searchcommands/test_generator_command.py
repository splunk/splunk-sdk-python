import io
import time

from splunklib.searchcommands import Configuration, GeneratingCommand
from . import chunked_data_stream as chunky


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
    expected = set(str(i) for i in range(1, 10))
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


def test_allow_empty_input_for_generating_command():
    """
    Passing allow_empty_input for generating command will cause an error
    """

    @Configuration()
    class GeneratorTest(GeneratingCommand):
        def generate(self):
            for num in range(1, 3):
                yield {"_index": num}

    generator = GeneratorTest()
    in_stream = io.BytesIO()
    out_stream = io.BytesIO()

    try:
        generator.process([], in_stream, out_stream, allow_empty_input=False)
    except ValueError as error:
        assert str(error) == "allow_empty_input cannot be False for Generating Commands"


def test_all_fieldnames_present_for_generated_records():
    @Configuration()
    class GeneratorTest(GeneratingCommand):
        def generate(self):
            yield self.gen_record(_time=time.time(), one=1)
            yield self.gen_record(_time=time.time(), two=2)
            yield self.gen_record(_time=time.time(), three=3)
            yield self.gen_record(_time=time.time(), four=4)
            yield self.gen_record(_time=time.time(), five=5)

    generator = GeneratorTest()
    in_stream = io.BytesIO()
    in_stream.write(chunky.build_getinfo_chunk())
    in_stream.write(chunky.build_chunk({'action': 'execute'}))
    in_stream.seek(0)
    out_stream = io.BytesIO()
    generator._process_protocol_v2([], in_stream, out_stream)
    out_stream.seek(0)

    ds = chunky.ChunkedDataStream(out_stream)
    fieldnames_expected = {'_time', 'one', 'two', 'three', 'four', 'five'}
    fieldnames_actual = set()
    for chunk in ds:
        for row in chunk.data:
            fieldnames_actual |= set(row.keys())
    assert fieldnames_expected.issubset(fieldnames_actual)
