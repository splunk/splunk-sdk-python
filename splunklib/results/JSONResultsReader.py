from io import BufferedReader
from json import loads as json_loads
from .Message import Message


class JSONResultsReader:
    """This class returns dictionaries and Splunk messages from a JSON results
    stream.
    ``JSONResultsReader`` is iterable, and returns a ``dict`` for results, or a
    :class:`Message` object for Splunk messages. This class has one field,
    ``is_preview``, which is ``True`` when the results are a preview from a
    running search, or ``False`` when the results are from a completed search.

    This function has no network activity other than what is implicit in the
    stream it operates on.

    :param `stream`: The stream to read from (any object that supports``.read()``).

    **Example**::

        import results
        response = ... # the body of an HTTP response
        reader = results.JSONResultsReader(response)
        for result in reader:
            if isinstance(result, dict):
                print(f"Result: {result}")
            elif isinstance(result, results.Message):
                print(f"Message: {result}")
        print(f"is_preview = {reader.is_preview}")
    """

    # Be sure to update the docstrings of client.Jobs.oneshot,
    # client.Job.results_preview and client.Job.results to match any
    # changes made to JSONResultsReader.
    #
    # This wouldn't be a class, just the _parse_results function below,
    # except that you cannot get the current generator inside the
    # function creating that generator. Thus it's all wrapped up for
    # the sake of one field.
    def __init__(self, stream):
        # The search/jobs/exports endpoint, when run with
        # earliest_time=rt and latest_time=rt, output_mode=json, streams a sequence of
        # JSON documents, each containing a result, as opposed to one
        # results element containing lots of results.
        stream = BufferedReader(stream)
        self.is_preview = None
        self._gen = self._parse_results(stream)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._gen)

    def _parse_results(self, stream):
        """Parse results and messages out of *stream*."""
        msg_type = None
        text = None
        for line in stream.readlines():
            strip_line = line.strip()
            if strip_line.__len__() == 0: continue
            parsed_line = json_loads(strip_line)
            if "preview" in parsed_line:
                self.is_preview = parsed_line["preview"]
            if "messages" in parsed_line and parsed_line["messages"].__len__() > 0:
                for message in parsed_line["messages"]:
                    msg_type = message.get("type", "Unknown Message Type")
                    text = message.get("text")
                yield Message(msg_type, text)
            if "result" in parsed_line:
                yield parsed_line["result"]
            if "results" in parsed_line:
                for result in parsed_line["results"]:
                    yield result
