from .Collection import Collection

from splunklib.entity import Job
from splunklib.exceptions import NotSupportedError

from splunklib.client.utils import _load_atom_entries, _parse_atom_entry, _load_sid
from splunklib.constants import PATH_JOBS_V2, PATH_JOBS


class Jobs(Collection):
    """This class represents a collection of search jobs. Retrieve this
    collection using :meth:`Service.jobs`."""

    def __init__(self, service):
        # Splunk 9 introduces the v2 endpoint
        if not service.disable_v2_api:
            path = PATH_JOBS_V2
        else:
            path = PATH_JOBS
        Collection.__init__(self, service, path, item=Job)
        # The count value to say list all the contents of this
        # Collection is 0, not -1 as it is on most.
        self.null_count = 0

    def _load_list(self, response):
        # Overridden because Job takes a sid instead of a path.
        entries = _load_atom_entries(response)
        if entries is None: return []
        entities = []
        for entry in entries:
            state = _parse_atom_entry(entry)
            entity = self.item(
                self.service,
                entry['content']['sid'],
                state=state)
            entities.append(entity)
        return entities

    def create(self, query, **kwargs):
        """ Creates a search using a search query and any additional parameters
        you provide.

        :param query: The search query.
        :type query: ``string``
        :param kwargs: Additiona parameters (optional). For a list of available
            parameters, see `Search job parameters
            <http://dev.splunk.com/view/SP-CAAAEE5#searchjobparams>`_
            on Splunk Developer Portal.
        :type kwargs: ``dict``

        :return: The :class:`Job`.
        """
        if kwargs.get("exec_mode", None) == "oneshot":
            raise TypeError("Cannot specify exec_mode=oneshot; use the oneshot method instead.")
        response = self.post(search=query, **kwargs)
        sid = _load_sid(response, kwargs.get("output_mode", None))
        return Job(self.service, sid)

    def export(self, query, **params):
        """Runs a search and immediately starts streaming preview events. This method returns a streaming handle to
        this job's events as an XML document from the server. To parse this stream into usable Python objects,
        pass the handle to :class:`splunklib.results.JSONResultsReader` along with the query param
        "output_mode='json'"::

            import splunklib.client as client
            import splunklib.results as results
            service = client.connect(...)
            rr = results.JSONResultsReader(service.jobs.export("search * | head 5",output_mode='json'))
            for result in rr:
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    print(f'{result.type}: {result.message}')
                elif isinstance(result, dict):
                    # Normal events are returned as dicts
                    print(result)
            assert rr.is_preview == False

        Running an export search is more efficient as it streams the results
        directly to you, rather than having to write them out to disk and make
        them available later. As soon as results are ready, you will receive
        them.

        The ``export`` method makes a single roundtrip to the server (as opposed
        to two for :meth:`create` followed by :meth:`preview`), plus at most two
        more if the ``autologin`` field of :func:`connect` is set to ``True``.

        :raises `ValueError`: Raised for invalid queries.
        :param query: The search query.
        :type query: ``string``
        :param params: Additional arguments (optional). For a list of valid
            parameters, see `GET search/jobs/export
            <http://docs/Documentation/Splunk/latest/RESTAPI/RESTsearch#search.2Fjobs.2Fexport>`_
            in the REST API documentation.
        :type params: ``dict``

        :return: The ``InputStream`` IO handle to raw XML returned from the server.
        """
        if "exec_mode" in params:
            raise TypeError("Cannot specify an exec_mode to export.")
        params['segmentation'] = params.get('segmentation', 'none')
        return self.post(path_segment="export",
                         search=query,
                         **params).body

    def itemmeta(self):
        """There is no metadata available for class:``Jobs``.

        Any call to this method raises a class:``NotSupportedError``.

        :raises: class:``NotSupportedError``
        """
        raise NotSupportedError()

    def oneshot(self, query, **params):
        """Run a oneshot search and returns a streaming handle to the results.

        The ``InputStream`` object streams fragments from the server. To parse this stream into usable Python
        objects, pass the handle to :class:`splunklib.results.JSONResultsReader` along with the query param
        "output_mode='json'" ::

            import splunklib.client as client
            import splunklib.results as results
            service = client.connect(...)
            rr = results.JSONResultsReader(service.jobs.oneshot("search * | head 5",output_mode='json'))
            for result in rr:
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    print(f'{result.type}: {result.message}')
                elif isinstance(result, dict):
                    # Normal events are returned as dicts
                    print(result)
            assert rr.is_preview == False

        The ``oneshot`` method makes a single roundtrip to the server (as opposed
        to two for :meth:`create` followed by :meth:`results`), plus at most two more
        if the ``autologin`` field of :func:`connect` is set to ``True``.

        :raises ValueError: Raised for invalid queries.

        :param query: The search query.
        :type query: ``string``
        :param params: Additional arguments (optional):

            - "output_mode": Specifies the output format of the results (XML,
              JSON, or CSV).

            - "earliest_time": Specifies the earliest time in the time range to
              search. The time string can be a UTC time (with fractional seconds),
              a relative time specifier (to now), or a formatted time string.

            - "latest_time": Specifies the latest time in the time range to
              search. The time string can be a UTC time (with fractional seconds),
              a relative time specifier (to now), or a formatted time string.

            - "rf": Specifies one or more fields to add to the search.

        :type params: ``dict``

        :return: The ``InputStream`` IO handle to raw XML returned from the server.
        """
        if "exec_mode" in params:
            raise TypeError("Cannot specify an exec_mode to oneshot.")
        params['segmentation'] = params.get('segmentation', 'none')
        return self.post(search=query,
                         exec_mode="oneshot",
                         **params).body
