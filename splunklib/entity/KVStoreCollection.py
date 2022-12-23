import json

from .Entity import Entity
from splunklib.client import KVStoreCollectionData


class KVStoreCollection(Entity):
    @property
    def data(self):
        """Returns data object for this Collection.

        :rtype: :class:`KVStoreCollectionData`
        """
        return KVStoreCollectionData(self)

    def update_index(self, name, value):
        """Changes the definition of a KV Store index.

        :param name: name of index to change
        :type name: ``string``
        :param value: new index definition
        :type value: ``dict`` or ``string``

        :return: Result of POST request
        """
        kwargs = {}
        kwargs['index.' + name] = value if isinstance(value, str) else json.dumps(value)
        return self.post(**kwargs)

    def update_field(self, name, value):
        """Changes the definition of a KV Store field.

        :param name: name of field to change
        :type name: ``string``
        :param value: new field definition
        :type value: ``string``

        :return: Result of POST request
        """
        kwargs = {}
        kwargs['field.' + name] = value
        return self.post(**kwargs)
