import json

from .Collection import Collection
from splunklib.entity import KVStoreCollection


class KVStoreCollections(Collection):
    def __init__(self, service):
        Collection.__init__(self, service, 'storage/collections/config', item=KVStoreCollection)

    def create(self, name, indexes={}, fields={}, **kwargs):
        """Creates a KV Store Collection.

        :param name: name of collection to create
        :type name: ``string``
        :param indexes: dictionary of index definitions
        :type indexes: ``dict``
        :param fields: dictionary of field definitions
        :type fields: ``dict``
        :param kwargs: a dictionary of additional parameters specifying indexes and field definitions
        :type kwargs: ``dict``

        :return: Result of POST request
        """
        for k, v in list(indexes.items()):
            if isinstance(v, dict):
                v = json.dumps(v)
            kwargs['index.' + k] = v
        for k, v in list(fields.items()):
            kwargs['field.' + k] = v
        return self.post(name=name, **kwargs)
