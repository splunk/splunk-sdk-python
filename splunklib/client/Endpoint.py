import re

from splunklib.binding import UrlEncoded
from splunklib.constants import PATH_JOBS, PATH_JOBS_V2


class Endpoint:
    """This class represents individual Splunk resources in the Splunk REST API.

    An ``Endpoint`` object represents a URI, such as ``/services/saved/searches``.
    This class provides the common functionality of :class:`Collection` and
    :class:`Entity` (essentially HTTP GET and POST methods).
    """

    def __init__(self, service, path):
        self.service = service
        self.path = path

    def get_api_version(self, path):
        """Return the API version of the service used in the provided path.

        Args:
            path (str): A fully-qualified endpoint path (for example, "/services/search/jobs").

        Returns:
            int: Version of the API (for example, 1)
        """
        # Default to v1 if undefined in the path
        # For example, "/services/search/jobs" is using API v1
        api_version = 1

        versionSearch = re.search('(?:servicesNS\/[^/]+\/[^/]+|services)\/[^/]+\/v(\d+)\/', path)
        if versionSearch:
            api_version = int(versionSearch.group(1))

        return api_version

    def get(self, path_segment="", owner=None, app=None, sharing=None, **query):
        """Performs a GET operation on the path segment relative to this endpoint.

        This method is named to match the HTTP method. This method makes at least
        one roundtrip to the server, one additional round trip for
        each 303 status returned, plus at most two additional round
        trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        If *owner*, *app*, and *sharing* are omitted, this method takes a
        default namespace from the :class:`Service` object for this :class:`Endpoint`.
        All other keyword arguments are included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Service`` is not logged in.
        :raises HTTPError: Raised when an error in the request occurs.
        :param path_segment: A path segment relative to this endpoint.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode for the namespace (optional).
        :type sharing: "global", "system", "app", or "user"
        :param query: All other keyword arguments, which are used as query
            parameters.
        :type query: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            import splunklib.client
            s = client.service(...)
            apps = s.apps
            apps.get() == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '26208'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:30:35 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            apps.get('nonexistant/path') # raises HTTPError
            s.logout()
            apps.get() # raises AuthenticationError
        """
        # self.path to the Endpoint is relative in the SDK, so passing
        # owner, app, sharing, etc. along will produce the correct
        # namespace in the final request.
        if path_segment.startswith('/'):
            path = path_segment
        else:
            if not self.path.endswith('/') and path_segment != "":
                self.path = self.path + '/'
            path = self.service._abspath(self.path + path_segment, owner=owner,
                                         app=app, sharing=sharing)
        # ^-- This was "%s%s" % (self.path, path_segment).
        # That doesn't work, because self.path may be UrlEncoded.

        # Get the API version from the path
        api_version = self.get_api_version(path)

        # Search API v2+ fallback to v1: - In v2+, /results_preview, /events and /results do not support search
        # params. - Fallback from v2+ to v1 if Splunk Version is < 9. if api_version >= 2 and ('search' in query and
        # path.endswith(tuple(["results_preview", "events", "results"])) or self.service.splunk_version < (9,
        # )): path = path.replace(PATH_JOBS_V2, PATH_JOBS)

        if api_version == 1:
            if isinstance(path, UrlEncoded):
                path = UrlEncoded(path.replace(PATH_JOBS_V2, PATH_JOBS), skip_encode=True)
            else:
                path = path.replace(PATH_JOBS_V2, PATH_JOBS)

        return self.service.get(path,
                                owner=owner, app=app, sharing=sharing,
                                **query)

    def post(self, path_segment="", owner=None, app=None, sharing=None, **query):
        """Performs a POST operation on the path segment relative to this endpoint.

        This method is named to match the HTTP method. This method makes at least
        one roundtrip to the server, one additional round trip for
        each 303 status returned, plus at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        If *owner*, *app*, and *sharing* are omitted, this method takes a
        default namespace from the :class:`Service` object for this :class:`Endpoint`.
        All other keyword arguments are included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Service`` is not logged in.
        :raises HTTPError: Raised when an error in the request occurs.
        :param path_segment: A path segment relative to this endpoint.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode of the namespace (optional).
        :type sharing: ``string``
        :param query: All other keyword arguments, which are used as query
            parameters.
        :type query: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            import splunklib.client
            s = client.service(...)
            apps = s.apps
            apps.post(name='boris') == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '2908'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 18:34:50 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'Created',
                 'status': 201}
            apps.get('nonexistant/path') # raises HTTPError
            s.logout()
            apps.get() # raises AuthenticationError
        """
        if path_segment.startswith('/'):
            path = path_segment
        else:
            if not self.path.endswith('/') and path_segment != "":
                self.path = self.path + '/'
            path = self.service._abspath(self.path + path_segment, owner=owner, app=app, sharing=sharing)

        # Get the API version from the path
        api_version = self.get_api_version(path)

        # Search API v2+ fallback to v1: - In v2+, /results_preview, /events and /results do not support search
        # params. - Fallback from v2+ to v1 if Splunk Version is < 9. if api_version >= 2 and ('search' in query and
        # path.endswith(tuple(["results_preview", "events", "results"])) or self.service.splunk_version < (9,
        # )): path = path.replace(PATH_JOBS_V2, PATH_JOBS)

        if api_version == 1:
            if isinstance(path, UrlEncoded):
                path = UrlEncoded(path.replace(PATH_JOBS_V2, PATH_JOBS), skip_encode=True)
            else:
                path = path.replace(PATH_JOBS_V2, PATH_JOBS)

        return self.service.post(path, owner=owner, app=app, sharing=sharing, **query)
