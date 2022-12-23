import json

from splunklib.binding import UrlEncoded


class KVStoreCollectionData:
    """This class represents the data endpoint for a KVStoreCollections.

    Retrieve using :meth:`KVStoreCollection.data`
    """
    JSON_HEADER = [('Content-Type', 'application/json')]

    def __init__(self, collection):
        self.service = collection.service
        self.collection = collection
        self.owner, self.app, self.sharing = collection._proper_namespace()
        self.path = 'storage/collections/data/' + UrlEncoded(self.collection.name, encode_slash=True) + '/'

    def _get(self, url, **kwargs):
        return self.service.get(self.path + url, owner=self.owner, app=self.app, sharing=self.sharing, **kwargs)

    def _post(self, url, **kwargs):
        return self.service.post(self.path + url, owner=self.owner, app=self.app, sharing=self.sharing, **kwargs)

    def _delete(self, url, **kwargs):
        return self.service.delete(self.path + url, owner=self.owner, app=self.app, sharing=self.sharing, **kwargs)

    def query(self, **query):
        """
        Gets the results of query, with optional parameters sort, limit, skip, and fields.

        :param query: Optional parameters. Valid options are sort, limit, skip, and fields
        :type query: ``dict``

        :return: Array of documents retrieved by query.
        :rtype: ``array``
        """

        for key, value in list(query.items()):
            if isinstance(query[key], dict):
                query[key] = json.dumps(value)

        return json.loads(self._get('', **query).body.read().decode('utf-8'))

    def query_by_id(self, id):
        """
        Returns object with _id = id.

        :param id: Value for ID. If not a string will be coerced to string.
        :type id: ``string``

        :return: Document with id
        :rtype: ``dict``
        """
        return json.loads(self._get(UrlEncoded(str(id), encode_slash=True)).body.read().decode('utf-8'))

    def insert(self, data):
        """
        Inserts item into this collection. An _id field will be generated if not assigned in the data.

        :param data: Document to insert
        :type data: ``string``

        :return: _id of inserted object
        :rtype: ``dict``
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        return json.loads(
            self._post('', headers=KVStoreCollectionData.JSON_HEADER, body=data).body.read().decode('utf-8'))

    def delete(self, query=None):
        """
        Deletes all data in collection if query is absent. Otherwise, deletes all data matched by query.

        :param query: Query to select documents to delete
        :type query: ``string``

        :return: Result of DELETE request
        """
        return self._delete('', **({'query': query}) if query else {})

    def delete_by_id(self, id):
        """
        Deletes document that has _id = id.

        :param id: id of document to delete
        :type id: ``string``

        :return: Result of DELETE request
        """
        return self._delete(UrlEncoded(str(id), encode_slash=True))

    def update(self, id, data):
        """
        Replaces document with _id = id with data.

        :param id: _id of document to update
        :type id: ``string``
        :param data: the new document to insert
        :type data: ``string``

        :return: id of replaced document
        :rtype: ``dict``
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        return json.loads(self._post(UrlEncoded(str(id), encode_slash=True), headers=KVStoreCollectionData.JSON_HEADER,
                                     body=data).body.read().decode('utf-8'))

    def batch_find(self, *dbqueries):
        """
        Returns array of results from queries dbqueries.

        :param dbqueries: Array of individual queries as dictionaries
        :type dbqueries: ``array`` of ``dict``

        :return: Results of each query
        :rtype: ``array`` of ``array``
        """
        if len(dbqueries) < 1:
            raise Exception('Must have at least one query.')

        data = json.dumps(dbqueries)

        return json.loads(
            self._post('batch_find', headers=KVStoreCollectionData.JSON_HEADER, body=data).body.read().decode('utf-8'))

    def batch_save(self, *documents):
        """
        Inserts or updates every document specified in documents.

        :param documents: Array of documents to save as dictionaries
        :type documents: ``array`` of ``dict``

        :return: Results of update operation as overall stats
        :rtype: ``dict``
        """
        if len(documents) < 1:
            raise Exception('Must have at least one document.')

        data = json.dumps(documents)

        return json.loads(
            self._post('batch_save', headers=KVStoreCollectionData.JSON_HEADER, body=data).body.read().decode('utf-8'))
