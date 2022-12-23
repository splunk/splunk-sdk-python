from .Collection import Collection
from .ConfigurationFile import ConfigurationFile

from splunklib.exceptions import HTTPError, IllegalOperationException
from splunklib.constants import PATH_CONF, PATH_PROPERTIES
from ..entity import Stanza


class Configurations(Collection):
    """This class provides access to the configuration files from this Splunk
    instance. Retrieve this collection using :meth:`Service.confs`.

    Splunk's configuration is divided into files, and each file into
    stanzas. This collection is unusual in that the values in it are
    themselves collections of :class:`ConfigurationFile` objects.
    """

    def __init__(self, service):
        Collection.__init__(self, service, PATH_PROPERTIES, item=ConfigurationFile)
        if self.service.namespace.owner == '-' or self.service.namespace.app == '-':
            raise ValueError("Configurations cannot have wildcards in namespace.")

    def __getitem__(self, key):
        # The superclass implementation is designed for collections that contain
        # entities. This collection (Configurations) contains collections
        # (ConfigurationFile).
        #
        # The configurations endpoint returns multiple entities when we ask for a single file.
        # This screws up the default implementation of __getitem__ from Collection, which thinks
        # that multiple entities means a name collision, so we have to override it here.
        try:
            response = self.get(key)
            return ConfigurationFile(self.service, PATH_CONF % key, state={'title': key})
        except HTTPError as he:
            if he.status == 404:  # No entity matching key
                raise KeyError(key)
            else:
                raise

    def __contains__(self, key):
        # configs/conf-{name} never returns a 404. We have to post to properties/{name}
        # in order to find out if a configuration exists.
        try:
            response = self.get(key)
            return True
        except HTTPError as he:
            if he.status == 404:  # No entity matching key
                return False
            raise

    def create(self, name):
        """ Creates a configuration file named *name*.

        If there is already a configuration file with that name,
        the existing file is returned.

        :param name: The name of the configuration file.
        :type name: ``string``

        :return: The :class:`ConfigurationFile` object.
        """
        # This has to be overridden to handle the plumbing of creating
        # a ConfigurationFile (which is a Collection) instead of some
        # Entity.
        if not isinstance(name, str):
            raise ValueError(f"Invalid name: {repr(name)}")
        response = self.post(__conf=name)
        if response.status == 303:
            return self[name]
        if response.status == 201:
            return ConfigurationFile(self.service, PATH_CONF % name, item=Stanza, state={'title': name})
        raise ValueError(f"Unexpected status code {response.status} returned from creating a stanza")

    def delete(self, key):
        """Raises `IllegalOperationException`."""
        raise IllegalOperationException("Cannot delete configuration files from the REST API.")

    def _entity_path(self, state):
        # Overridden to make all the ConfigurationFile objects
        # returned refer to the configs/ path instead of the
        # properties/ path used by Configrations.
        return PATH_CONF % state['title']
