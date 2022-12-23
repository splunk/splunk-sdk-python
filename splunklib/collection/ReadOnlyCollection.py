import logging
from urllib import parse

from splunklib.binding import UrlEncoded
from splunklib.client import Endpoint
from splunklib.entity import Entity
from splunklib.exceptions import AmbiguousReferenceException, HTTPError

from splunklib.client.utils import _load_atom, _load_atom_entries, _parse_atom_entry, _parse_atom_metadata, _trailing
from splunklib.constants import MATCH_ENTRY_CONTENT


logger = logging.getLogger(__name__)


class ReadOnlyCollection(Endpoint):
    """This class represents a read-only collection of entities in the Splunk
    instance.
    """

    def __init__(self, service, path, item=Entity):
        Endpoint.__init__(self, service, path)
        self.item = item  # Item accessor
        self.null_count = -1

    def __contains__(self, name):
        """Is there at least one entry called *name* in this collection?

        Makes a single roundtrip to the server, plus at most two more
        if
        the ``autologin`` field of :func:`connect` is set to ``True``.
        """
        try:
            self[name]
            return True
        except KeyError:
            return False
        except AmbiguousReferenceException:
            return True

    def __getitem__(self, key):
        """Fetch an item named *key* from this collection.

        A name is not a unique identifier in a collection. The unique
        identifier is a name plus a namespace. For example, there can
        be a saved search named ``'mysearch'`` with sharing ``'app'``
        in application ``'search'``, and another with sharing
        ``'user'`` with owner ``'boris'`` and application
        ``'search'``. If the ``Collection`` is attached to a
        ``Service`` that has ``'-'`` (wildcard) as user and app in its
        namespace, then both of these may be visible under the same
        name.

        Where there is no conflict, ``__getitem__`` will fetch the
        entity given just the name. If there is a conflict, and you
        pass just a name, it will raise a ``ValueError``. In that
        case, add the namespace as a second argument.

        This function makes a single roundtrip to the server, plus at
        most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param key: The name to fetch, or a tuple (name, namespace).
        :return: An :class:`Entity` object.
        :raises KeyError: Raised if *key* does not exist.
        :raises ValueError: Raised if no namespace is specified and *key*
                            does not refer to a unique name.

        **Example**::

            s = client.connect(...)
            saved_searches = s.saved_searches
            x1 = saved_searches.create(
                'mysearch', 'search * | head 1',
                owner='admin', app='search', sharing='app')
            x2 = saved_searches.create(
                'mysearch', 'search * | head 1',
                owner='admin', app='search', sharing='user')
            # Raises ValueError:
            saved_searches['mysearch']
            # Fetches x1
            saved_searches[
                'mysearch',
                client.namespace(sharing='app', app='search')]
            # Fetches x2
            saved_searches[
                'mysearch',
                client.namespace(sharing='user', owner='boris', app='search')]
        """
        try:
            if isinstance(key, tuple) and len(key) == 2:
                # x[a,b] is translated to x.__getitem__( (a,b) ), so we
                # have to extract values out.
                key, ns = key
                key = UrlEncoded(key, encode_slash=True)
                response = self.get(key, owner=ns.owner, app=ns.app)
            else:
                key = UrlEncoded(key, encode_slash=True)
                response = self.get(key)
            entries = self._load_list(response)
            if len(entries) > 1:
                raise AmbiguousReferenceException(
                    f"Found multiple entities named '{key}'; please specify a namespace.")
            if len(entries) == 0:
                raise KeyError(key)
            return entries[0]
        except HTTPError as he:
            if he.status == 404:  # No entity matching key and namespace.
                raise KeyError(key)
            else:
                raise

    def __iter__(self, **kwargs):
        """Iterate over the entities in the collection.

        :param kwargs: Additional arguments.
        :type kwargs: ``dict``
        :rtype: iterator over entities.

        Implemented to give Collection a listish interface. This
        function always makes a roundtrip to the server, plus at most
        two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            saved_searches = c.saved_searches
            for entity in saved_searches:
                print(f"Saved search named {entity.name}")
        """

        for item in self.iter(**kwargs):
            yield item

    def __len__(self):
        """Enable ``len(...)`` for ``Collection`` objects.

        Implemented for consistency with a listish interface. No
        further failure modes beyond those possible for any method on
        an Endpoint.

        This function always makes a round trip to the server, plus at
        most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            saved_searches = c.saved_searches
            n = len(saved_searches)
        """
        return len(self.list())

    def _entity_path(self, state):
        """Calculate the path to an entity to be returned.

        *state* should be the dictionary returned by
        :func:`_parse_atom_entry`. :func:`_entity_path` extracts the
        link to this entity from *state*, and strips all the namespace
        prefixes from it to leave only the relative path of the entity
        itself, sans namespace.

        :rtype: ``string``
        :return: an absolute path
        """
        # This has been factored out so that it can be easily
        # overloaded by Configurations, which has to switch its
        # entities' endpoints from its own properties/ to configs/.
        raw_path = parse.unquote(state.links.alternate)
        if 'servicesNS/' in raw_path:
            return _trailing(raw_path, 'servicesNS/', '/', '/')
        if 'services/' in raw_path:
            return _trailing(raw_path, 'services/')
        return raw_path

    def _load_list(self, response):
        """Converts *response* to a list of entities.

        *response* is assumed to be a :class:`Record` containing an
        HTTP response, of the form::

            {'status': 200,
             'headers': [('content-length', '232642'),
                         ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                         ('server', 'Splunkd'),
                         ('connection', 'close'),
                         ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                         ('date', 'Tue, 29 May 2012 15:27:08 GMT'),
                         ('content-type', 'text/xml; charset=utf-8')],
             'reason': 'OK',
             'body': ...a stream implementing .read()...}

        The ``'body'`` key refers to a stream containing an Atom feed,
        that is, an XML document with a toplevel element ``<feed>``,
        and within that element one or more ``<entry>`` elements.
        """
        # Some subclasses of Collection have to override this because
        # splunkd returns something that doesn't match
        # <feed><entry></entry><feed>.
        entries = _load_atom_entries(response)
        if entries is None: return []
        entities = []
        for entry in entries:
            state = _parse_atom_entry(entry)
            entity = self.item(
                self.service,
                self._entity_path(state),
                state=state)
            entities.append(entity)

        return entities

    def itemmeta(self):
        """Returns metadata for members of the collection.

        Makes a single roundtrip to the server, plus two more at most if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :return: A :class:`splunklib.data.Record` object containing the metadata.

        **Example**::

            import splunklib.client as client
            import pprint
            s = client.connect(...)
            pprint.pprint(s.apps.itemmeta())
            {'access': {'app': 'search',
                                    'can_change_perms': '1',
                                    'can_list': '1',
                                    'can_share_app': '1',
                                    'can_share_global': '1',
                                    'can_share_user': '1',
                                    'can_write': '1',
                                    'modifiable': '1',
                                    'owner': 'admin',
                                    'perms': {'read': ['*'], 'write': ['admin']},
                                    'removable': '0',
                                    'sharing': 'user'},
             'fields': {'optional': ['author',
                                        'configured',
                                        'description',
                                        'label',
                                        'manageable',
                                        'template',
                                        'visible'],
                                        'required': ['name'], 'wildcard': []}}
        """
        response = self.get("_new")
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return _parse_atom_metadata(content)

    def iter(self, offset=0, count=None, pagesize=None, **kwargs):
        """Iterates over the collection.

        This method is equivalent to the :meth:`list` method, but
        it returns an iterator and can load a certain number of entities at a
        time from the server.

        :param offset: The index of the first entity to return (optional).
        :type offset: ``integer``
        :param count: The maximum number of entities to return (optional).
        :type count: ``integer``
        :param pagesize: The number of entities to load (optional).
        :type pagesize: ``integer``
        :param kwargs: Additional arguments (optional):

            - "search" (``string``): The search query to filter responses.

            - "sort_dir" (``string``): The direction to sort returned items:
              "asc" or "desc".

            - "sort_key" (``string``): The field to use for sorting (optional).

            - "sort_mode" (``string``): The collating sequence for sorting
              returned items: "auto", "alpha", "alpha_case", or "num".

        :type kwargs: ``dict``

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            for saved_search in s.saved_searches.iter(pagesize=10):
                # Loads 10 saved searches at a time from the
                # server.
                ...
        """
        assert pagesize is None or pagesize > 0
        if count is None:
            count = self.null_count
        fetched = 0
        while count == self.null_count or fetched < count:
            response = self.get(count=pagesize or count, offset=offset, **kwargs)
            items = self._load_list(response)
            N = len(items)
            fetched += N
            for item in items:
                yield item
            if pagesize is None or N < pagesize:
                break
            offset += N
            logger.debug("pagesize=%d, fetched=%d, offset=%d, N=%d, kwargs=%s", pagesize, fetched, offset, N, kwargs)

    # kwargs: count, offset, search, sort_dir, sort_key, sort_mode
    def list(self, count=None, **kwargs):
        """Retrieves a list of entities in this collection.

        The entire collection is loaded at once and is returned as a list. This
        function makes a single roundtrip to the server, plus at most two more if
        the ``autologin`` field of :func:`connect` is set to ``True``.
        There is no caching--every call makes at least one round trip.

        :param count: The maximum number of entities to return (optional).
        :type count: ``integer``
        :param kwargs: Additional arguments (optional):

            - "offset" (``integer``): The offset of the first item to return.

            - "search" (``string``): The search query to filter responses.

            - "sort_dir" (``string``): The direction to sort returned items:
              "asc" or "desc".

            - "sort_key" (``string``): The field to use for sorting (optional).

            - "sort_mode" (``string``): The collating sequence for sorting
              returned items: "auto", "alpha", "alpha_case", or "num".

        :type kwargs: ``dict``
        :return: A ``list`` of entities.
        """
        # response = self.get(count=count, **kwargs)
        # return self._load_list(response)
        return list(self.iter(count=count, **kwargs))
