from .Collection import Collection

from splunklib.entity import SavedSearch
from splunklib.constants import PATH_SAVED_SEARCHES


class SavedSearches(Collection):
    """This class represents a collection of saved searches. Retrieve this
    collection using :meth:`Service.saved_searches`."""

    def __init__(self, service):
        Collection.__init__(
            self, service, PATH_SAVED_SEARCHES, item=SavedSearch)

    def create(self, name, search, **kwargs):
        """ Creates a saved search.

        :param name: The name for the saved search.
        :type name: ``string``
        :param search: The search query.
        :type search: ``string``
        :param kwargs: Additional arguments (optional). For a list of available
            parameters, see `Saved search parameters
            <http://dev.splunk.com/view/SP-CAAAEE5#savedsearchparams>`_
            on Splunk Developer Portal.
        :type kwargs: ``dict``
        :return: The :class:`SavedSearches` collection.
        """
        return Collection.create(self, name, search=search, **kwargs)
