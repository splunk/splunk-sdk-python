from .Entity import Entity
from splunklib.exceptions import HTTPError

from splunklib.client.utils import _load_atom
from splunklib.constants import PATH_JOBS, PATH_JOBS_V2


class Job(Entity):
    """This class represents a search job."""

    def __init__(self, service, sid, **kwargs):
        # Default to v2 in Splunk Version 9+
        path = "{path}{sid}"
        # Formatting path based on the Splunk Version
        if service.disable_v2_api:
            path = path.format(path=PATH_JOBS, sid=sid)
        else:
            path = path.format(path=PATH_JOBS_V2, sid=sid)

        Entity.__init__(self, service, path, skip_refresh=True, **kwargs)
        self.sid = sid

    # The Job entry record is returned at the root of the response
    def _load_atom_entry(self, response):
        return _load_atom(response).entry

    def cancel(self):
        """Stops the current search and deletes the results cache.

        :return: The :class:`Job`.
        """
        try:
            self.post("control", action="cancel")
        except HTTPError as he:
            if he.status == 404:
                # The job has already been cancelled, so
                # cancelling it twice is a nop.
                pass
            else:
                raise
        return self

    def disable_preview(self):
        """Disables preview for this job.

        :return: The :class:`Job`.
        """
        self.post("control", action="disablepreview")
        return self

    def enable_preview(self):
        """Enables preview for this job.

        **Note**: Enabling preview might slow search considerably.

        :return: The :class:`Job`.
        """
        self.post("control", action="enablepreview")
        return self

    def events(self, **kwargs):
        """Returns a streaming handle to this job's events.

        :param kwargs: Additional parameters (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/events
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fevents>`_
            in the REST API documentation.
        :type kwargs: ``dict``

        :return: The ``InputStream`` IO handle to this job's events.
        """
        kwargs['segmentation'] = kwargs.get('segmentation', 'none')

        # Search API v1(GET) and v2(POST)
        if self.service.disable_v2_api:
            return self.get("events", **kwargs).body
        return self.post("events", **kwargs).body

    def finalize(self):
        """Stops the job and provides intermediate results for retrieval.

        :return: The :class:`Job`.
        """
        self.post("control", action="finalize")
        return self

    def is_done(self):
        """Indicates whether this job finished running.

        :return: ``True`` if the job is done, ``False`` if not.
        :rtype: ``boolean``
        """
        if not self.is_ready():
            return False
        done = (self._state.content['isDone'] == '1')
        return done

    def is_ready(self):
        """Indicates whether this job is ready for querying.

        :return: ``True`` if the job is ready, ``False`` if not.
        :rtype: ``boolean``

        """
        response = self.get()
        if response.status == 204:
            return False
        self._state = self.read(response)
        ready = self._state.content['dispatchState'] not in ['QUEUED', 'PARSING']
        return ready

    @property
    def name(self):
        """Returns the name of the search job, which is the search ID (SID).

        :return: The search ID.
        :rtype: ``string``
        """
        return self.sid

    def pause(self):
        """Suspends the current search.

        :return: The :class:`Job`.
        """
        self.post("control", action="pause")
        return self

    def results(self, **query_params):
        """Returns a streaming handle to this job's search results. To get a nice, Pythonic iterator, pass the handle
        to :class:`splunklib.results.JSONResultsReader` along with the query param "output_mode='json'", as in::

            import splunklib.client as client
            import splunklib.results as results
            from time import sleep
            service = client.connect(...)
            job = service.jobs.create("search * | head 5")
            while not job.is_done():
                sleep(.2)
            rr = results.JSONResultsReader(job.results(output_mode='json'))
            for result in rr:
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    print(f'{result.type}: {result.message}')
                elif isinstance(result, dict):
                    # Normal events are returned as dicts
                    print(result)
            assert rr.is_preview == False

        Results are not available until the job has finished. If called on
        an unfinished job, the result is an empty event set.

        This method makes a single roundtrip
        to the server, plus at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param query_params: Additional parameters (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/results
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults>`_.
        :type query_params: ``dict``

        :return: The ``InputStream`` IO handle to this job's results.
        """
        query_params['segmentation'] = query_params.get('segmentation', 'none')

        # Search API v1(GET) and v2(POST)
        if self.service.disable_v2_api:
            return self.get("results", **query_params).body
        return self.post("results", **query_params).body

    def preview(self, **query_params):
        """Returns a streaming handle to this job's preview search results.

        Unlike :class:`splunklib.results.JSONResultsReader`along with the query param "output_mode='json'",
        which requires a job to be finished to return any results, the ``preview`` method returns any results that
        have been generated so far, whether the job is running or not. The returned search results are the raw data
        from the server. Pass the handle returned to :class:`splunklib.results.JSONResultsReader` to get a nice,
        Pythonic iterator over objects, as in::

            import splunklib.client as client
            import splunklib.results as results
            service = client.connect(...)
            job = service.jobs.create("search * | head 5")
            rr = results.JSONResultsReader(job.preview(output_mode='json'))
            for result in rr:
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    print(f'{result.type}: {result.message}')
                elif isinstance(result, dict):
                    # Normal events are returned as dicts
                    print(result)
            if rr.is_preview:
                print("Preview of a running search job.")
            else:
                print("Job is finished. Results are final.")

        This method makes one roundtrip to the server, plus at most
        two more if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param query_params: Additional parameters (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/results_preview
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults_preview>`_
            in the REST API documentation.
        :type query_params: ``dict``

        :return: The ``InputStream`` IO handle to this job's preview results.
        """
        query_params['segmentation'] = query_params.get('segmentation', 'none')

        # Search API v1(GET) and v2(POST)
        if self.service.disable_v2_api:
            return self.get("results_preview", **query_params).body
        return self.post("results_preview", **query_params).body

    def searchlog(self, **kwargs):
        """Returns a streaming handle to this job's search log.

        :param `kwargs`: Additional parameters (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/search.log
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fsearch.log>`_
            in the REST API documentation.
        :type kwargs: ``dict``

        :return: The ``InputStream`` IO handle to this job's search log.
        """
        return self.get("search.log", **kwargs).body

    def set_priority(self, value):
        """Sets this job's search priority in the range of 0-10.

        Higher numbers indicate higher priority. Unless splunkd is
        running as *root*, you can only decrease the priority of a running job.

        :param `value`: The search priority.
        :type value: ``integer``

        :return: The :class:`Job`.
        """
        self.post('control', action="setpriority", priority=value)
        return self

    def summary(self, **kwargs):
        """Returns a streaming handle to this job's summary.

        :param `kwargs`: Additional parameters (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/summary
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fsummary>`_
            in the REST API documentation.
        :type kwargs: ``dict``

        :return: The ``InputStream`` IO handle to this job's summary.
        """
        return self.get("summary", **kwargs).body

    def timeline(self, **kwargs):
        """Returns a streaming handle to this job's timeline results.

        :param `kwargs`: Additional timeline arguments (optional). For a list of valid
            parameters, see `GET search/jobs/{search_id}/timeline
            <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Ftimeline>`_
            in the REST API documentation.
        :type kwargs: ``dict``

        :return: The ``InputStream`` IO handle to this job's timeline.
        """
        return self.get("timeline", **kwargs).body

    def touch(self):
        """Extends the expiration time of the search to the current time (now) plus
        the time-to-live (ttl) value.

        :return: The :class:`Job`.
        """
        self.post("control", action="touch")
        return self

    def set_ttl(self, value):
        """Set the job's time-to-live (ttl) value, which is the time before the
        search job expires and is still available.

        :param `value`: The ttl value, in seconds.
        :type value: ``integer``

        :return: The :class:`Job`.
        """
        self.post("control", action="setttl", ttl=value)
        return self

    def unpause(self):
        """Resumes the current search, if paused.

        :return: The :class:`Job`.
        """
        self.post("control", action="unpause")
        return self
