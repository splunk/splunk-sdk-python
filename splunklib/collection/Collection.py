from .ReadOnlyCollection import ReadOnlyCollection
from splunklib.binding import UrlEncoded
from splunklib.client.utils import _load_atom, _parse_atom_entry, _path
from splunklib.constants import XNAME_ENTRY
from splunklib.exceptions import HTTPError, InvalidNameException


class Collection(ReadOnlyCollection):
    """A collection of entities.

    Splunk provides a number of different collections of distinct
    entity types: applications, saved searches, fired alerts, and a
    number of others. Each particular type is available separately
    from the Splunk instance, and the entities of that type are
    returned in a :class:`Collection`.

    The interface for :class:`Collection` does not quite match either
    ``list`` or ``dict`` in Python, because there are enough semantic
    mismatches with either to make its behavior surprising. A unique
    element in a :class:`Collection` is defined by a string giving its
    name plus namespace (although the namespace is optional if the name is
    unique).

    **Example**::

        import splunklib.client as client
        service = client.connect(...)
        mycollection = service.saved_searches
        mysearch = mycollection['my_search', client.namespace(owner='boris', app='natasha', sharing='user')]
        # Or if there is only one search visible named 'my_search'
        mysearch = mycollection['my_search']

    Similarly, ``name`` in ``mycollection`` works as you might expect (though
    you cannot currently pass a namespace to the ``in`` operator), as does
    ``len(mycollection)``.

    However, as an aggregate, :class:`Collection` behaves more like a
    list. If you iterate over a :class:`Collection`, you get an
    iterator over the entities, not the names and namespaces.

    **Example**::

        for entity in mycollection:
            assert isinstance(entity, client.Entity)

    Use the :meth:`create` and :meth:`delete` methods to create and delete
    entities in this collection. To view the access control list and other
    metadata of the collection, use the :meth:`ReadOnlyCollection.itemmeta` method.

    :class:`Collection` does no caching. Each call makes at least one
    round trip to the server to fetch data.
    """

    # def __init__(self, service, path, item):
    #     ReadOnlyCollection.__init__(self, service, path, item)

    def create(self, name, **params):
        """Creates a new entity in this collection.

        This function makes either one or two roundtrips to the
        server, depending on the type of entities in this
        collection, plus at most two more if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param name: The name of the entity to create.
        :type name: ``string``
        :param namespace: A namespace, as created by the :func:`splunklib.binding.namespace`
            function (optional).  You can also set ``owner``, ``app``, and
            ``sharing`` in ``params``.
        :type namespace: A :class:`splunklib.data.Record` object with keys ``owner``, ``app``,
            and ``sharing``.
        :param params: Additional entity-specific arguments (optional).
        :type params: ``dict``
        :return: The new entity.
        :rtype: A subclass of :class:`Entity`, chosen by :meth:`Collection.self.item`.

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            applications = s.apps
            new_app = applications.create("my_fake_app")
        """
        if not isinstance(name, str):
            raise InvalidNameException(f"{name} is not a valid name for an entity.")
        if 'namespace' in params:
            namespace = params.pop('namespace')
            params['owner'] = namespace.owner
            params['app'] = namespace.app
            params['sharing'] = namespace.sharing
        response = self.post(name=name, **params)
        atom = _load_atom(response, XNAME_ENTRY)
        if atom is None:
            # This endpoint doesn't return the content of the new
            # item. We have to go fetch it ourselves.
            return self[name]
        entry = atom.entry
        state = _parse_atom_entry(entry)
        entity = self.item(
            self.service,
            self._entity_path(state),
            state=state)
        return entity

    def delete(self, name, **params):
        """Deletes a specified entity from the collection.

        :param name: The name of the entity to delete.
        :type name: ``string``
        :return: The collection.
        :rtype: ``self``

        This method is implemented for consistency with the REST API's DELETE
        method.

        If there is no *name* entity on the server, a ``KeyError`` is
        thrown. This function always makes a roundtrip to the server.

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            saved_searches = c.saved_searches
            saved_searches.create('my_saved_search',
                                  'search * | head 1')
            assert 'my_saved_search' in saved_searches
            saved_searches.delete('my_saved_search')
            assert 'my_saved_search' not in saved_searches
        """
        name = UrlEncoded(name, encode_slash=True)
        if 'namespace' in params:
            namespace = params.pop('namespace')
            params['owner'] = namespace.owner
            params['app'] = namespace.app
            params['sharing'] = namespace.sharing
        try:
            self.service.delete(_path(self.path, name), **params)
        except HTTPError as he:
            # An HTTPError with status code 404 means that the entity
            # has already been deleted, and we reraise it as a
            # KeyError.
            if he.status == 404:
                raise KeyError(f"No such entity {name}")
            else:
                raise
        return self

    def get(self, name="", owner=None, app=None, sharing=None, **query):
        """Performs a GET request to the server on the collection.

        If *owner*, *app*, and *sharing* are omitted, this method takes a
        default namespace from the :class:`Service` object for this :class:`Endpoint`.
        All other keyword arguments are included in the URL as query parameters.

        :raises AuthenticationError: Raised when the ``Service`` is not logged in.
        :raises HTTPError: Raised when an error in the request occurs.
        :param path_segment: A path segment relative to this endpoint.
        :type path_segment: ``string``
        :param owner: The owner context of the namespace (optional).
        :type owner: ``string``
        :param app: The app context of the namespace (optional).
        :type app: ``string``
        :param sharing: The sharing mode for the namespace (optional).
        :type sharing: "global", "system", "app", or "user"
        :param query: All other keyword arguments, which are used as query
            parameters.
        :type query: ``string``
        :return: The response from the server.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``,
                and ``status``

        **Example**::

            import splunklib.client
            s = client.service(...)
            saved_searches = s.saved_searches
            saved_searches.get("my/saved/search") == \\
                {'body': ...a response reader object...,
                 'headers': [('content-length', '26208'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:30:35 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            saved_searches.get('nonexistant/search') # raises HTTPError
            s.logout()
            saved_searches.get() # raises AuthenticationError

        """
        name = UrlEncoded(name, encode_slash=True)
        return super().get(name, owner, app, sharing, **query)
