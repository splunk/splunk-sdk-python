from io import BytesIO
from .HTTPError import HTTPError


class AuthenticationError(HTTPError):
    """Raised when a login request to Splunk fails.

    If your username was unknown or you provided an incorrect password
    in a call to :meth:`Context.login` or :meth:`splunklib.client.Service.login`,
    this exception is raised.
    """

    def __init__(self, message, cause):
        # Put the body back in the response so that HTTPError's constructor can
        # read it again.
        cause._response.body = BytesIO(cause.body)

        HTTPError.__init__(self, cause._response, message)
