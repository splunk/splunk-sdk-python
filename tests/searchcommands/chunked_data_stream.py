import collections
import csv
import io
import json

import splunklib.searchcommands.internals


class Chunk:
    def __init__(self, version, meta, data):
        self.version = version
        self.meta = json.loads(meta)
        dialect = splunklib.searchcommands.internals.CsvDialect
        self.data = csv.DictReader(io.StringIO(data.decode("utf-8")),
                                   dialect=dialect)


class ChunkedDataStreamIter(collections.abc.Iterator):
    def __init__(self, chunk_stream):
        self.chunk_stream = chunk_stream

    def __next__(self):
        return next(self)

    def __next__(self):
        try:
            return self.chunk_stream.read_chunk()
        except EOFError:
            raise StopIteration


class ChunkedDataStream(collections.abc.Iterable):
    def __iter__(self):
        return ChunkedDataStreamIter(self)

    def __init__(self, stream):
        empty = stream.read(0)
        assert isinstance(empty, bytes)
        self.stream = stream

    def read_chunk(self):
        header = self.stream.readline()

        while len(header) > 0 and header.strip() == b'':
            header = self.stream.readline()  # Skip empty lines
        if len(header) == 0:
            raise EOFError

        version, meta, data = header.rstrip().split(b',')
        metabytes = self.stream.read(int(meta))
        databytes = self.stream.read(int(data))
        return Chunk(version, metabytes, databytes)


def build_chunk(keyval, data=None):
    metadata = json.dumps(keyval).encode('utf-8')
    data_output = _build_data_csv(data)
    return b"chunked 1.0,%d,%d\n%s%s" % (len(metadata), len(data_output), metadata, data_output)


def build_empty_searchinfo():
    return {
        'earliest_time': 0,
        'latest_time': 0,
        'search': "",
        'dispatch_dir': "",
        'sid': "",
        'args': [],
        'splunk_version': "42.3.4",
    }


def build_getinfo_chunk():
    return build_chunk({
        'action': 'getinfo',
        'preview': False,
        'searchinfo': build_empty_searchinfo()})


def build_data_chunk(data, finished=True):
    return build_chunk({'action': 'execute', 'finished': finished}, data)


def _build_data_csv(data):
    if data is None:
        return b''
    if isinstance(data, bytes):
        return data
    csvout = io.StringIO()

    headers = set()
    for datum in data:
        headers.update(list(datum.keys()))
    writer = csv.DictWriter(csvout, headers,
                            dialect=splunklib.searchcommands.internals.CsvDialect)
    writer.writeheader()
    for datum in data:
        writer.writerow(datum)
    return csvout.getvalue().encode('utf-8')
