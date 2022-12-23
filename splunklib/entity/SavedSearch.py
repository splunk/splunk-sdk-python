from datetime import datetime

from .AlertGroup import AlertGroup
from .Entity import Entity
from .Job import Job

from splunklib import collection
from splunklib.exceptions import IllegalOperationException
from splunklib.client.utils import _load_sid, _load_atom_entries, _parse_atom_entry
from splunklib.constants import PATH_FIRED_ALERTS


class SavedSearch(Entity):
    """This class represents a saved search."""

    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def acknowledge(self):
        """Acknowledges the suppression of alerts from this saved search and
        resumes alerting.

        :return: The :class:`SavedSearch`.
        """
        self.post("acknowledge")
        return self

    @property
    def alert_count(self):
        """Returns the number of alerts fired by this saved search.

        :return: The number of alerts fired by this saved search.
        :rtype: ``integer``
        """
        return int(self._state.content.get('triggered_alert_count', 0))

    def dispatch(self, **kwargs):
        """Runs the saved search and returns the resulting search job.

        :param `kwargs`: Additional dispatch arguments (optional). For details,
                         see the `POST saved/searches/{name}/dispatch
                         <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTsearch#POST_saved.2Fsearches.2F.7Bname.7D.2Fdispatch>`_
                         endpoint in the REST API documentation.
        :type kwargs: ``dict``
        :return: The :class:`Job`.
        """
        response = self.post("dispatch", **kwargs)
        sid = _load_sid(response, kwargs.get("output_mode", None))
        return Job(self.service, sid)

    @property
    def fired_alerts(self):
        """Returns the collection of fired alerts (a fired alert group)
        corresponding to this saved search's alerts.

        :raises IllegalOperationException: Raised when the search is not scheduled.

        :return: A collection of fired alerts.
        :rtype: :class:`AlertGroup`
        """
        if self['is_scheduled'] == '0':
            raise IllegalOperationException('Unscheduled saved searches have no alerts.')
        c = collection.Collection(
            self.service,
            self.service._abspath(PATH_FIRED_ALERTS + self.name,
                                  owner=self._state.access.owner,
                                  app=self._state.access.app,
                                  sharing=self._state.access.sharing),
            item=AlertGroup)
        return c

    def history(self, **kwargs):
        """Returns a list of search jobs corresponding to this saved search.

        :param `kwargs`: Additional arguments (optional).
        :type kwargs: ``dict``

        :return: A list of :class:`Job` objects.
        """
        response = self.get("history", **kwargs)
        entries = _load_atom_entries(response)
        if entries is None:
            return []
        jobs = []
        for entry in entries:
            job = Job(self.service, entry.title)
            jobs.append(job)
        return jobs

    def update(self, search=None, **kwargs):
        """Updates the server with any changes you've made to the current saved
        search along with any additional arguments you specify.

        :param `search`: The search query (optional).
        :type search: ``string``
        :param `kwargs`: Additional arguments (optional). For a list of available
            parameters, see `Saved search parameters
            <http://dev.splunk.com/view/SP-CAAAEE5#savedsearchparams>`_
            on Splunk Developer Portal.
        :type kwargs: ``dict``

        :return: The :class:`SavedSearch`.
        """
        # Updates to a saved search *require* that the search string be
        # passed, so we pass the current search string if a value wasn't
        # provided by the caller.
        if search is None:
            search = self.content.search
        Entity.update(self, search=search, **kwargs)
        return self

    def scheduled_times(self, earliest_time='now', latest_time='+1h'):
        """Returns the times when this search is scheduled to run.

        By default this method returns the times in the next hour. For different
        time ranges, set *earliest_time* and *latest_time*. For example,
        for all times in the last day use "earliest_time=-1d" and
        "latest_time=now".

        :param earliest_time: The earliest time.
        :type earliest_time: ``string``
        :param latest_time: The latest time.
        :type latest_time: ``string``

        :return: The list of search times.
        """
        response = self.get("scheduled_times",
                            earliest_time=earliest_time,
                            latest_time=latest_time)
        data = self._load_atom_entry(response)
        rec = _parse_atom_entry(data)
        times = [datetime.fromtimestamp(int(t))
                 for t in rec.content.scheduled_times]
        return times

    def suppress(self, expiration):
        """Skips any scheduled runs of this search in the next *expiration*
        number of seconds.

        :param expiration: The expiration period, in seconds.
        :type expiration: ``integer``

        :return: The :class:`SavedSearch`.
        """
        self.post("suppress", expiration=expiration)
        return self

    @property
    def suppressed(self):
        """Returns the number of seconds that this search is blocked from running
        (possibly 0).

        :return: The number of seconds.
        :rtype: ``integer``
        """
        r = self._run_action("suppress")
        if r.suppressed == "1":
            return int(r.expiration)
        return 0

    def unsuppress(self):
        """Cancels suppression and makes this search run as scheduled.

        :return: The :class:`SavedSearch`.
        """
        self.post("suppress", expiration="0")
        return self
