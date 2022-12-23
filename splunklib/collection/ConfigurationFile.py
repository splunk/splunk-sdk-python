from .Collection import Collection
from splunklib.entity import Stanza


class ConfigurationFile(Collection):
    """This class contains all of the stanzas from one configuration file.
    """

    # __init__'s arguments must match those of an Entity, not a
    # Collection, since it is being created as the elements of a
    # Configurations, which is a Collection subclass.
    def __init__(self, service, path, **kwargs):
        Collection.__init__(self, service, path, item=Stanza)
        self.name = kwargs['state']['title']
