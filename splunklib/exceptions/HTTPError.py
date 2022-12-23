# Note: the error response schema supports multiple messages but we only
# return the first, although we do return the body so that an exception
# handler that wants to read multiple messages can do so.
from xml.etree.ElementTree import XML, ParseError


class HTTPError(Exception):
    """This exception is raised for HTTP responses that return an error."""

    def __init__(self, response, _message=None):
        status = response.status
        reason = response.reason
        body = response.body.read()
        try:
            detail = XML(body).findtext("./messages/msg")
        except ParseError:
            detail = body
        detail_formatted = "" if detail is None else f" -- {detail}"
        message = f"HTTP {status} {reason}{detail_formatted}"
        Exception.__init__(self, _message or message)
        self.status = status
        self.reason = reason
        self.headers = response.headers
        self.body = body
        self._response = response
