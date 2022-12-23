from splunklib.binding import UrlEncoded
from splunklib.client import Endpoint
from splunklib.exceptions import AmbiguousReferenceException, IncomparableException, IllegalOperationException

from splunklib.client.utils import _load_atom, _parse_atom_entry
from splunklib.constants import XNAME_ENTRY


# kwargs: path, app, owner, sharing, state
class Entity(Endpoint):
    """This class is a base class for Splunk entities in the REST API, such as
    saved searches, jobs, indexes, and inputs.

    ``Entity`` provides the majority of functionality required by entities.
    Subclasses only implement the special cases for individual entities.
    For example for saved searches, the subclass makes fields like ``action.email``,
    ``alert_type``, and ``search`` available.

    An ``Entity`` is addressed like a dictionary, with a few extensions,
    so the following all work, for example in saved searches::

        ent['action.email']
        ent['alert_type']
        ent['search']

    You can also access the fields as though they were the fields of a Python
    object, as in::

        ent.alert_type
        ent.search

    However, because some of the field names are not valid Python identifiers,
    the dictionary-like syntax is preferable.

    The state of an :class:`Entity` object is cached, so accessing a field
    does not contact the server. If you think the values on the
    server have changed, call the :meth:`Entity.refresh` method.
    """
    # Not every endpoint in the API is an Entity or a Collection. For
    # example, a saved search at saved/searches/{name} has an additional
    # method saved/searches/{name}/scheduled_times, but this isn't an
    # entity in its own right. In these cases, subclasses should
    # implement a method that uses the get and post methods inherited
    # from Endpoint, calls the _load_atom function (it's elsewhere in
    # client.py, but not a method of any object) to read the
    # information, and returns the extracted data in a Pythonesque form.
    #
    # The primary use of subclasses of Entity is to handle specially
    # named fields in the Entity. If you only need to provide a default
    # value for an optional field, subclass Entity and define a
    # dictionary ``defaults``. For instance,::
    #
    #     class Hypothetical(Entity):
    #         defaults = {'anOptionalField': 'foo',
    #                     'anotherField': 'bar'}
    #
    # If you have to do more than provide a default, such as rename or
    # actually process values, then define a new method with the
    # ``@property`` decorator.
    #
    #     class Hypothetical(Entity):
    #         @property
    #         def foobar(self):
    #             return self.content['foo'] + "-" + self.content["bar"]

    # Subclasses can override defaults the default values for
    # optional fields. See above.
    defaults = {}

    def __init__(self, service, path, **kwargs):
        Endpoint.__init__(self, service, path)
        self._state = None
        if not kwargs.get('skip_refresh', False):
            self.refresh(kwargs.get('state', None))  # "Refresh"

    def __contains__(self, item):
        try:
            self[item]
            return True
        except (KeyError, AttributeError):
            return False

    def __eq__(self, other):
        """Raises IncomparableException.

        Since Entity objects are snapshots of times on the server, no
        simple definition of equality will suffice beyond instance
        equality, and instance equality leads to strange situations
        such as::

            import splunklib.client as client
            c = client.connect(...)
            saved_searches = c.saved_searches
            x = saved_searches['asearch']

        but then ``x != saved_searches['asearch']``.

        whether or not there was a change on the server. Rather than
        try to do something fancy, we simply declare that equality is
        undefined for Entities.

        Makes no roundtrips to the server.
        """
        raise IncomparableException(f"Equality is undefined for objects of class {self.__class__.__name__}")

    def __getattr__(self, key):
        # Called when an attribute was not found by the normal method. In this
        # case we try to find it in self.content and then self.defaults.
        if key in self.state.content:
            return self.state.content[key]
        if key in self.defaults:
            return self.defaults[key]
        raise AttributeError(key)

    def __getitem__(self, key):
        # getattr attempts to find a field on the object in the normal way,
        # then calls __getattr__ if it cannot.
        return getattr(self, key)

    # Load the Atom entry record from the given response - this is a method
    # because the "entry" record varies slightly by entity and this allows
    # for a subclass to override and handle any special cases.
    def _load_atom_entry(self, response):
        elem = _load_atom(response, XNAME_ENTRY)
        if isinstance(elem, list):
            apps = [ele.entry.content.get('eai:appName') for ele in elem]

            raise AmbiguousReferenceException(
                f"Fetch from server returned multiple entries for name '{elem[0].entry.title}' in apps {apps}.")
        return elem.entry

    # Load the entity state record from the given response
    def _load_state(self, response):
        entry = self._load_atom_entry(response)
        return _parse_atom_entry(entry)

    def _run_action(self, path_segment, **kwargs):
        """Run a method and return the content Record from the returned XML.

        A method is a relative path from an Entity that is not itself
        an Entity. _run_action assumes that the returned XML is an
        Atom field containing one Entry, and the contents of Entry is
        what should be the return value. This is right in enough cases
        to make this method useful.
        """
        response = self.get(path_segment, **kwargs)
        data = self._load_atom_entry(response)
        rec = _parse_atom_entry(data)
        return rec.content

    def _proper_namespace(self, owner=None, app=None, sharing=None):
        """Produce a namespace sans wildcards for use in entity requests.

        This method tries to fill in the fields of the namespace which are `None`
        or wildcard (`'-'`) from the entity's namespace. If that fails, it uses
        the service's namespace.

        :param owner:
        :param app:
        :param sharing:
        :return:
        """
        if owner is None and app is None and sharing is None:  # No namespace provided
            if self._state is not None and 'access' in self._state:
                return (self._state.access.owner,
                        self._state.access.app,
                        self._state.access.sharing)
            return (self.service.namespace['owner'],
                    self.service.namespace['app'],
                    self.service.namespace['sharing'])
        return owner, app, sharing

    def delete(self):
        owner, app, sharing = self._proper_namespace()
        return self.service.delete(self.path, owner=owner, app=app, sharing=sharing)

    def get(self, path_segment="", owner=None, app=None, sharing=None, **query):
        owner, app, sharing = self._proper_namespace(owner, app, sharing)
        return super().get(path_segment, owner=owner, app=app, sharing=sharing, **query)

    def post(self, path_segment="", owner=None, app=None, sharing=None, **query):
        owner, app, sharing = self._proper_namespace(owner, app, sharing)
        return super().post(path_segment, owner=owner, app=app, sharing=sharing, **query)

    def refresh(self, state=None):
        """Refreshes the state of this entity.

        If *state* is provided, load it as the new state for this
        entity. Otherwise, make a roundtrip to the server (by calling
        the :meth:`read` method of ``self``) to fetch an updated state,
        plus at most two additional round trips if
        the ``autologin`` field of :func:`connect` is set to ``True``.

        :param state: Entity-specific arguments (optional).
        :type state: ``dict``
        :raises EntityDeletedException: Raised if the entity no longer exists on
            the server.

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            search = s.apps['search']
            search.refresh()
        """
        if state is not None:
            self._state = state
        else:
            self._state = self.read(self.get())
        return self

    @property
    def access(self):
        """Returns the access metadata for this entity.

        :return: A :class:`splunklib.data.Record` object with three keys:
            ``owner``, ``app``, and ``sharing``.
        """
        return self.state.access

    @property
    def content(self):
        """Returns the contents of the entity.

        :return: A ``dict`` containing values.
        """
        return self.state.content

    def disable(self):
        """Disables the entity at this endpoint."""
        self.post("disable")
        return self

    def enable(self):
        """Enables the entity at this endpoint."""
        self.post("enable")
        return self

    @property
    def fields(self):
        """Returns the content metadata for this entity.

        :return: A :class:`splunklib.data.Record` object with three keys:
            ``required``, ``optional``, and ``wildcard``.
        """
        return self.state.fields

    @property
    def links(self):
        """Returns a dictionary of related resources.

        :return: A ``dict`` with keys and corresponding URLs.
        """
        return self.state.links

    @property
    def name(self):
        """Returns the entity name.

        :return: The entity name.
        :rtype: ``string``
        """
        return self.state.title

    def read(self, response):
        """ Reads the current state of the entity from the server. """
        results = self._load_state(response)
        # In lower layers of the SDK, we end up trying to URL encode
        # text to be dispatched via HTTP. However, these links are already
        # URL encoded when they arrive, and we need to mark them as such.
        unquoted_links = dict((k, UrlEncoded(v, skip_encode=True))
                              for k, v in list(results['links'].items()))
        results['links'] = unquoted_links
        return results

    def reload(self):
        """Reloads the entity."""
        self.post("_reload")
        return self

    def acl_update(self, **kwargs):
        """To update Access Control List (ACL) properties for an endpoint.

        :param kwargs: Additional entity-specific arguments (required).

            - "owner" (``string``): The Splunk username, such as "admin". A value of "nobody" means no specific user
            (required).

            - "sharing" (``string``): A mode that indicates how the resource is shared. The sharing mode can be
            "user", "app", "global", or "system" (required).

        :type kwargs: ``dict``

        **Example**::

            import splunklib.client as client
            service = client.connect(...)
            saved_search = service.saved_searches["name"]
            saved_search.acl_update(sharing="app", owner="nobody", app="search", **{"perms.read": "admin, nobody"})
        """
        if "body" not in kwargs:
            kwargs = {"body": kwargs}

        if "sharing" not in kwargs["body"]:
            raise ValueError("Required argument 'sharing' is missing.")
        if "owner" not in kwargs["body"]:
            raise ValueError("Required argument 'owner' is missing.")

        self.post("acl", **kwargs)
        self.refresh()
        return self

    @property
    def state(self):
        """Returns the entity's state record.

        :return: A ``dict`` containing fields and metadata for the entity.
        """
        if self._state is None:
            self.refresh()
        return self._state

    def update(self, **kwargs):
        """Updates the server with any changes you've made to the current entity
        along with any additional arguments you specify.

            **Note**: You cannot update the ``name`` field of an entity.

        Many of the fields in the REST API are not valid Python
        identifiers, which means you cannot pass them as keyword
        arguments. That is, Python will fail to parse the following::

            # This fails
            x.update(check-new=False, email.to='boris@utopia.net')

        However, you can always explicitly use a dictionary to pass
        such keys::

            # This works
            x.update(**{'check-new': False, 'email.to': 'boris@utopia.net'})

        :param kwargs: Additional entity-specific arguments (optional).
        :type kwargs: ``dict``

        :return: The entity this method is called on.
        :rtype: class:`Entity`
        """
        # The peculiarity in question: the REST API creates a new
        # Entity if we pass name in the dictionary, instead of the
        # expected behavior of updating this Entity. Therefore, we
        # check for 'name' in kwargs and throw an error if it is
        # there.
        if 'name' in kwargs:
            raise IllegalOperationException('Cannot update the name of an Entity via the REST API.')
        self.post(**kwargs)
        return self
