from .Collection import Collection
from splunklib.exceptions import NotSupportedError

from splunklib.constants import PATH_LOGGER


class Loggers(Collection):
    """This class represents a collection of service logging categories.
    Retrieve this collection using :meth:`Service.loggers`."""

    def __init__(self, service):
        Collection.__init__(self, service, PATH_LOGGER)

    def itemmeta(self):
        """There is no metadata available for class:``Loggers``.

        Any call to this method raises a class:``NotSupportedError``.

        :raises: class:``NotSupportedError``
        """
        raise NotSupportedError()
