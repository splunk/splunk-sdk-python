# Copyright 2011-2012 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

#
# The purpose of this module is to provide a friendlier domain interface to 
# various Splunk endpoints. The approach here is to leverage the binding
# layer to capture endpoint context and provide objects and methods that
# offer simplified access their corresponding endpoints. The design avoids
# caching resource state. From the perspective of this module, the 'policy'
# for caching resource state belongs in the application or a higher level
# framework, and its the purpose of this module to provide simplified
# access to that resource state.
#
# A side note, the objects below that provide helper methods for updating eg:
# Entity state, are written so that they may be used in a fluent style.
#

"""A Pythonic interface to the Splunk REST API.

``splunklib.client`` wraps a Pythonic layer around the wire level
binding of ``splunklib.binding``. The core of the library is the
``Service`` class that encapsulates a connection to the server, and
provides access to the various aspects of the REST API. Typically you
would create a server with the :func:`connect` function, as in::

    import splunklib.client as client
    s = client.connect(host='localhost', port=8089, 
                       username='admin', password='...')
    assert isinstance(s, client.Service)
    
``Service``s have fields for the various API functionality (``apps``,
``saved_searches``, etc.). All these fields are ``Collection``s. For
example,::

    a = s.apps
    my_app = a.create('my_app')
    my_app = a['my_app']
    a.delete('my_app')

The individual applications, or elements of the other ``Collection``s,
are subclasses of ``Entity``. An ``Entity`` has fields giving its
attributes, and methods specific to each kind of entity.::

    print my_app['author'] # or print my_app.author
    my_app.package() # Create a compressed package of this application
"""

# UNDONE: Add Collection.refresh and list caching
# UNDONE: Resolve conflict between Collection.delete and name of REST method
# UNDONE: Add Endpoint.delete
# UNDONE: Add Entity.remove

import datetime
import json
import urllib
import logging
from time import sleep
from datetime import datetime, timedelta
import socket
import contextlib

from binding import Context, HTTPError, AuthenticationError, namespace, UrlEncoded
from data import record
import data

__all__ = [
    "connect",
    "NotSupportedError",
    "OperationError",
    "IncomparableException",
    "Service"
]

PATH_APPS = "apps/local/"
PATH_CAPABILITIES = "authorization/capabilities/"
PATH_CONF = "configs/conf-%s/"
PATH_PROPERTIES = "properties/"
PATH_DEPLOYMENT_CLIENTS = "deployment/client/"
PATH_DEPLOYMENT_TENANTS = "deployment/tenants/"
PATH_DEPLOYMENT_SERVERS = "deployment/server/"
PATH_DEPLOYMENT_SERVERCLASSES = "deployment/serverclass/"
PATH_EVENT_TYPES = "saved/eventtypes/"
PATH_FIRED_ALERTS = "alerts/fired_alerts/"
PATH_INDEXES = "data/indexes/"
PATH_INPUTS = "data/inputs/"
PATH_JOBS = "search/jobs/"
PATH_LOGGER = "server/logger/"
PATH_MESSAGES = "messages/"
PATH_MODULAR_INPUTS = "data/modular-inputs"
PATH_ROLES = "authentication/roles/"
PATH_SAVED_SEARCHES = "saved/searches/"
PATH_STANZA = "configs/conf-%s/%s" # (file, stanza)
PATH_USERS = "authentication/users/"
PATH_RECEIVERS_STREAM = "receivers/stream"
PATH_RECEIVERS_SIMPLE = "receivers/simple"

XNAMEF_ATOM = "{http://www.w3.org/2005/Atom}%s"
XNAME_ENTRY = XNAMEF_ATOM % "entry"
XNAME_CONTENT = XNAMEF_ATOM % "content"

MATCH_ENTRY_CONTENT = "%s/%s/*" % (XNAME_ENTRY, XNAME_CONTENT)

class NoSuchUserException(Exception):
    pass

class NoSuchApplicationException(Exception):
    pass

class IllegalOperationException(Exception):
    pass

class IncomparableException(Exception):
    pass

class JobNotReadyException(Exception):
    pass

class AmbiguousReferenceException(ValueError):
    pass

class EntityDeletedException(Exception):
    pass

class InvalidNameException(Exception):
    pass

class OperationFailedException(Exception):
    pass

class NoSuchCapability(Exception):
    pass

def trailing(template, *targets):
    """Substring of *template* following all *targets*.

    Most easily explained by example::

        template = "this is a test of the bunnies."
        trailing(template, "is", "est", "the") == \
            " bunnies"

    Each target is matched successively in the string, and the string
    remaining after the last target is returned. If one of the targets
    fails to match, a ValueError is raised.

    :param template: Template to extract a trailing string from.
    :type template: string
    :param targets: Strings to successively match in *template*.
    :type targets: strings
    :returns: Trailing string after all targets are matched.
    :rtype: string
    :raises ValueError: when one of the targets does not match.
    """
    s = template
    for t in targets:
        n = s.find(t)
        if n == -1:
            raise ValueError("Target " + t + " not found in template.")
        s = s[n + len(t):]
    return s

# Filter the given state content record according to the given arg list.
def _filter_content(content, *args):
    if len(args) > 0:
        return record((k, content[k]) for k in args)
    return record((k, v) for k, v in content.iteritems()
        if k not in ['eai:acl', 'eai:attributes', 'type'])

# Construct a resource path from the given base path + resource name
def _path(base, name):
    if not base.endswith('/'): base = base + '/'
    return base + name

# Load an atom record from the body of the given response
def _load_atom(response, match=None):
    return data.load(response.body.read(), match)

# Load an array of atom entries from the body of the given response
def _load_atom_entries(response):
    r = _load_atom(response)
    if 'feed' in r:
        # Need this to handle a random case in the REST API
        if r.feed.get('totalResults') == 0:
            return []
        entries = r.feed.get('entry', None)
        if entries is None: return None
        return entries if isinstance(entries, list) else [entries]
    # This rigamarole is because the jobs endpoint doesn't
    # returned an entry inside a feed, it just returns and entry.
    else: 
        entries = r.get('entry', None)
        if entries is None: return None
        return entries if isinstance(entries, list) else [entries]

# Load the sid from the body of the given response
def _load_sid(response):
    return _load_atom(response).response.sid

# Parse the given atom entry record into a generic entity state record
def _parse_atom_entry(entry):
    title = entry.get('title', None)

    elink = entry.get('link', [])
    elink = elink if isinstance(elink, list) else [elink]
    links = record((link.rel, link.href) for link in elink)

    # Retrieve entity content values
    content = entry.get('content', {})

    # Host entry metadata
    metadata = _parse_atom_metadata(content)

    # Filter some of the noise out of the content record
    content = record((k, v) for k, v in content.iteritems()
        if k not in ['eai:acl', 'eai:attributes', 'type'])

    return record({
        'title': title,
        'links': links,
        'access': metadata.access,
        'fields': metadata.fields,
        'content': content
    })

# Parse the metadata fields out of the given atom entry content record
def _parse_atom_metadata(content):
    # Hoist access metadata
    access = content.get('eai:acl', None)

    # Hoist content metadata (and cleanup some naming)
    attributes = content.get('eai:attributes', {})
    fields = record({
        'required': attributes.get('requiredFields', []),
        'optional': attributes.get('optionalFields', []),
        'wildcard': attributes.get('wildcardFields', [])})

    return record({'access': access, 'fields': fields})

# kwargs: scheme, host, port, app, owner, username, password
def connect(**kwargs):
    """Connect and log in to a Splunk instance.

    This is a shorthand for ``Service(...).login()``. :func:`connect`
    makes one round trip to the server (for logging in).

    :param `host`: The host name (default: ``"localhost"``).
    :type host: string
    :param `port`: The port number (default: 8089).
    :type port: integer
    :param `scheme`: The scheme for accessing the service (default: ``"https"``)
    :type scheme: ``"https"``
    :param `owner`: The owner namespace (optional).
    :type owner: string
    :param `app`: The app context (optional).
    :type app: string
    :param `token`: The current session token (optional). Session tokens can be 
                    shared across multiple service instances.
    :type token: string
    :param `username`: The Splunk account username, which is used to 
                       authenticate the Splunk instance.
    :type username: string
    :param `password`: The password, which is used to authenticate the Splunk 
                       instance.
    :type password: string
    :return: An initialized connection
    :rtype: :class:`Service`

    **Example**:

        import splunklib.client as client
        s = client.connect(...)
        a = s.apps["my_app"]
        ...
    """
    return Service(**kwargs).login()

class Service(Context):
    """A Pythonic binding to Splunk instances.

    A :class:`Service` represents a binding to a Splunk instane on an
    HTTP or HTTPS port. It handles the details of authentication, wire
    formats, and wraps the REST API endpoints into something more
    Pythonic. All the low level operations on the instance from
    :class:`splunklib.Context` are available as well in case you need
    to do something outside of what :class:`Service` provides.

    After creating a :class:`Service`, you must call its :meth:`login`
    method before you can issue useful requests to Splunk.
    Alternately, use the :func:`connect` function to create an already
    authenticated :class:`Service` object, or provide a session token
    when creating the :class:`Service` object explicitly (the same
    token may be shared by multiple :class:`Service` objects).

    :param `host`: The host name (default: ``"localhost"``).
    :type host: string
    :param `port`: The port number (default: 8089).
    :type port: int
    :param `scheme`: The scheme for accessing the service (default: ``"https"``)
    :type scheme: ``"https"`` or ``"http"``
    :param `owner`: The owner namespace (optional; use ``"-"`` for wildcard).
    :type owner: string
    :param `app`: The app context (optional; use ``"-"`` for wildcard).
    :type app: string
    :param `token`: The current session token (optional). Session tokens can be 
                    shared across multiple service instances.
    :type token: string
    :param `username`: The Splunk account username, which is used to 
                       authenticate the Splunk instance.
    :type username: string
    :param `password`: The password, which is used to authenticate the Splunk 
                       instance.
    :type password: string
    :returns: A :class:`Service` instance.

    **Example**::

        import splunklib.client as client
        s = client.Service(username="boris", password="natasha", ...)
        s.login()
        # Or equivalently
        s = client.connect(username="boris", password="natasha")
        # Or if you already have a session token
        s = client.Service(token="atg232342aa34324a")
    """
    def __init__(self, **kwargs):
        Context.__init__(self, **kwargs)
        self._splunk_version = None

    @property
    def apps(self):
        """The applications installed in this instance of Splunk.
       
        :rtype: :class:`Collection`
        """
        return Collection(self, PATH_APPS, item=Application)

    @property
    def confs(self):
        """The configuration files of this Splunk instance."""
        return Configurations(self)

    @property
    def capabilities(self):
        """Returns a list of system capabilities."""
        response = self.get(PATH_CAPABILITIES)
        return _load_atom(response, MATCH_ENTRY_CONTENT).capabilities

    @property
    def event_types(self):
        """The saved event types known by this Splunk instance."""
        return Collection(self, PATH_EVENT_TYPES)

    @property
    def fired_alerts(self):
        """Alerts that have been fired on the Splunk instance."""
        return Collection(self, PATH_FIRED_ALERTS, item=AlertGroup)

    @property
    def indexes(self):
        """The indexes of this Splunk instance."""
        return Indexes(self, PATH_INDEXES, item=Index)

    @property
    def info(self):
        """Returns information about the service."""
        response = self.get("server/info")
        return _filter_content(_load_atom(response, MATCH_ENTRY_CONTENT))

    @property
    def inputs(self):
        """The inputs configured on this Splunk instance."""
        return Inputs(self)

    @property
    def jobs(self):
        """Returns a collection of current search jobs."""
        return Jobs(self)

    @property
    def loggers(self):
        """Returns a collection of service logging categories and their status.
        """
        return Loggers(self)

    @property
    def messages(self):
        """Returns a collection of service messages."""
        return Collection(self, PATH_MESSAGES, item=Message)

    @property
    def modular_input_kinds(self):
        """Returns a collection of the modular input kinds on this Splunk instance."""
        if self.splunk_version[0] >= 5:
            return ReadOnlyCollection(self, PATH_MODULAR_INPUTS, item=ModularInputKind)
        else:
            raise IllegalOperationException("Modular inputs are not supported before Splunk version 5.")

    # kwargs: enable_lookups, reload_macros, parse_only, output_mode
    def parse(self, query, **kwargs):
        """Parses a search query and returns a semantic map of the search.

        :param `query`: The search query to parse.
        :param `kwargs`: Optional arguments to pass to the ``search/parser`` 
                         endpoint.
        :return: A semantic map of the parsed search query.
        """
        return self.get("search/parser", q=query, **kwargs)

    def restart(self, timeout=None):
        """Restarts this Splunk instance.

        The service will be unavailable until it has successfully
        restarted.

        If timeout is specified, `restart` blocks until the service
        comes back up or timeout is exceeded. Otherwise, restart returns immediately.
        """
        result = self.get("server/control/restart")
        if timeout is None: return result
        start = datetime.now()
        diff = timedelta(seconds=10)
        while datetime.now() - start < diff:
            try:
                self.login() # Has the server gone down yet?
                sleep(0.3)
            except Exception:
                break # Server is down. Move on.
        start = datetime.now()
        diff = timedelta(seconds=timeout)
        while datetime.now() - start < diff:
            try:
                self.login() # Awake yet?
                return result
            except Exception, e:
                sleep(2)
        raise Exception, "Operation timed out."

    @property
    def roles(self):
        """Returns a collection of user roles."""
        return Roles(self)

    def search(self, query, **kwargs):
        return self.jobs.create(query, **kwargs)

    @property
    def saved_searches(self):
        """Returns a collection of saved searches."""
        return SavedSearches(self)

    @property
    def settings(self):
        """Returns configuration settings for the service."""
        return Settings(self)

    @property
    def splunk_version(self):
        """Get the version of the splunkd instance this object is attached to.

        The version is returned as a 3-tuple of the version components as
        integers (i.e., `(4,3,3)` or `(5,0,0)`.
        """
        if self._splunk_version is None:
            self._splunk_version = tuple([int(p) for p in self.info['version'].split('.')])
        return self._splunk_version

    @property
    def users(self):
        """Returns a collection of users."""
        return Users(self)

class Endpoint(object):
    """Individual resources in the REST API.
    
    An Endpoint represents a URI, such as /services/saved/searches. It
    has provides the common functionality of Collection and Entity
    (essentially HTTP get and post methods).
    """
    def __init__(self, service, path):
        self.service = service
        self.path = path if path.endswith('/') else path + '/'

    def get(self, path_segment="", owner=None, app=None, sharing=None, **query):
        """GET from *path_segment* relative to this endpoint.

        Named to match the HTTP method. This function makes at least
        one roundtrip to the server, one additional round trip for
        each 303 status returned, plus at most two additional round
        trips if autologin is enabled.

        If *owner*, *app*, and *sharing* are omitted, then takes a
        default namespace from this ``Endpoint``'s ``Service``. All
        other keyword arguments are included in the URL as query
        parameters.

        :raises AuthenticationError: when a this Endpoint's ``Service`` is not logged in.
        :raises HTTPError: when there was an error in the request.
        :param path_segment: A path_segment relative to this endpoint to GET from (default: ``""``).
        :type path_segment: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :param query: All other keyword arguments, used as query parameters.
        :type query: values should be strings
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            import splunklib.client
            s = client.service(...)
            apps = s.apps
            apps.get() == \
                {'body': <splunklib.binding.ResponseReader at 0x10f8709d0>,
                 'headers': [('content-length', '26208'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 16:30:35 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'OK',
                 'status': 200}
            apps.get('nonexistant/path') # raises HTTPError
            s.logout()
            apps.get() # raises AuthenticationError
        """
        # self.path to the Endpoint is relative in the SDK, so passing
        # owner, app, sharing, etc. along will produce the correct
        # namespace in the final request.
        if path_segment.startswith('/'):
            path = path_segment
        else:
            path = self.service._abspath(self.path + path_segment, owner=owner, 
                                         app=app, sharing=sharing)
        # ^-- This was "%s%s" % (self.path, path_segment). 
        # That doesn't work, because self.path may be UrlEncoded.
        return self.service.get(path, 
                                owner=owner, app=app, sharing=sharing, 
                                **query)

    def post(self, path_segment="", owner=None, app=None, sharing=None, **query):
        """POST to *path_segment* relative to this endpoint.

        Named to match the HTTP method. This function makes at least
        one roundtrip to the server, one additional round trip for
        each 303 status returned, and at most two additional round
        trips if autologin is enabled.

        If *owner*, *app*, and *sharing* are omitted, then takes a
        default namespace from this ``Endpoint``'s ``Service``. All
        other keyword arguments are included in the URL as query
        parameters.

        :raises AuthenticationError: when a this Endpoint's ``Service`` is not logged in.
        :raises HTTPError: when there was an error in the request.
        :param path_segment: A path_segment relative to this endpoint to POST to (default: ``""``).
        :type path_segment: string
        :param owner, app, sharing: Namespace parameters (optional).
        :type owner, app, sharing: string
        :param query: All other keyword arguments, used as query parameters.
        :type query: values should be strings
        :return: The server's response.
        :rtype: ``dict`` with keys ``body``, ``headers``, ``reason``, 
                and ``status``

        **Example**::

            import splunklib.client
            s = client.service(...)
            apps = s.apps
            apps.post(name='boris') == \
                {'body': <splunklib.binding.ResponseReader at 0x10b348290>,
                 'headers': [('content-length', '2908'),
                             ('expires', 'Fri, 30 Oct 1998 00:00:00 GMT'),
                             ('server', 'Splunkd'),
                             ('connection', 'close'),
                             ('cache-control', 'no-store, max-age=0, must-revalidate, no-cache'),
                             ('date', 'Fri, 11 May 2012 18:34:50 GMT'),
                             ('content-type', 'text/xml; charset=utf-8')],
                 'reason': 'Created',
                 'status': 201}
            apps.get('nonexistant/path') # raises HTTPError
            s.logout()
            apps.get() # raises AuthenticationError
        """
        if path_segment.startswith('/'):
            path = path_segment
        else:
            path = self.service._abspath(self.path + path_segment, owner=owner, 
                                         app=app, sharing=sharing)
        return self.service.post(path, 
                                 owner=owner, app=app, sharing=sharing,
                                 **query)

# kwargs: path, app, owner, sharing, state
class Entity(Endpoint):
    """Base class for entities in the REST API such as saved searches or applications.

    Entity provides the majority of functionality required by entities
    in the REST API. Subclasses only implement the special cases for
    individual Entities, such as nicely making whitelists and
    blacklists in deployment serverclasses into Python lists.

    An Entity is addressed like a dictionary, with a few extensions,
    so the following all work::

        ent['email.action']
        ent['disabled']
        ent['whitelist']

    Many endpoints have values that share a prefix, such as
    ``email.to``, ``email.action``, ``email.subject``. You can extract
    the whole fields, or use the key ``email`` to get a dictionary of
    all the subelements. That is ``ent['email']`` will return a
    dictionary with the keys ``to``, ``action``, ``subject``, etc. If
    there are multiple levels of dots, then each level is made into a
    subdictionary, so ``email.body.salutation`` would be accessed at
    ``ent['email']['body']['salutation']`` or
    ``ent['email.body.salutation']``.

    Equivalently, you can also access the fields as if they were the
    fields of a Python object, as in::

        ent.email.action
        ent.disabled
        ent.whitelist

    However, since some of the field names are not valid Python identifiers,
    you should prefer the dictionary-like syntax.

    The state of an :class:`Entity` is cached, so accessing a field
    does not contact the server. If you expect the values on the
    server have changed, you have to call the :meth:`refresh` method
    on the :class:`Entity` before the updated values will be
    available.
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
            self.refresh(kwargs.get('state', None)) # "Prefresh"

    def __contains__(self, item):
        try:
            self[item]
            return True
        except KeyError:
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
        try to do something fancy, we simple declare that equality is
        undefined for Entities.

        Makes no roundtrips to the server.
        """
        raise IncomparableException(
            "Equality is undefined for objects of class %s" % \
                self.__class__.__name__)

    def __getattr__(self, key):
        # Called when an attribute was not found by the normal method. In this
        # case we try to find it in self.content and then self.defaults.
        if key in self.state.content:
            return self.state.content[key]
        elif key in self.defaults:
            return self.defaults[key]
        else:
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
            return [x.entry for x in elem]
        else:
            return elem.entry

    # Load the entity state record from the given response
    def _load_state(self, response):
        entry = self._load_atom_entry(response)
        if isinstance(entry, list):
            raise AmbiguousReferenceException("Fetch from server returned multiple entries for name %s." % self.name)
        else:
            return _parse_atom_entry(entry)

    def _run_method(self, path_segment, **kwargs):
        """Run a method and return the content Record from the returned XML.

        A method is a relative path from an Entity that is not itself
        an Entity. _run_method assumes that the returned XML is an
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

        This method handles the case of two entities with the same name in different namespaces
        showing up due to wildcards in the service's namespace. We replace the wildcards with the
        namespace of the entity we want.

        :param owner:
        :param app:
        :param sharing:
        :return:
        """
        if owner is None and app is None and sharing is None and\
            (self.service.namespace.owner == '-' or self.service.namespace.app == '-'):
            # If no namespace is specified and there are wildcards in the service's namespace,
            # we need to use the entity's namespace to avoid name collisions.
            if 'access' in self._state:
                owner = self._state.access.owner
                app = self._state.access.app
                sharing = self._state.access.sharing
        return (owner, app, sharing)


    def get(self, path_segment="", owner=None, app=None, sharing=None, **query):
        owner, app, sharing = self._proper_namespace(owner, app, sharing)
        return super(Entity, self).get(path_segment, owner=owner, app=app, sharing=sharing, **query)

    def post(self, path_segment="", owner=None, app=None, sharing=None, **query):
        owner, app, sharing = self._proper_namespace(owner, app, sharing)
        return super(Entity, self).post(path_segment, owner=owner, app=app, sharing=sharing, **query)

    def refresh(self, state=None):
        """Refresh the state of this entity.

        If *state* is provided, load it as the new state for this
        entity. Otherwise, make a roundtrip to the server (by calling
        the :meth:`read` method of self) to fetch an updated state,
        plus at most two additional round trips if autologin is
        enabled.

        Raises EntityDeletedException if the entity no longer exists on the server.

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            search = s.apps['search']
            search.refresh()
        """
        if state is not None:
            self._state = state
        else:
            try:
                raw_state = self.read()
            except HTTPError, he:
                if he.status == 404:
                    raise EntityDeletedException("Entity %s was already deleted" % self.name)
            raw_state['links'] = dict([(k, urllib.unquote(v)) for k,v in raw_state['links'].iteritems()])
            self._state = raw_state
        return self

    @property
    def access(self):
        """Returns entity access metadata."""
        return self.state.access

    @property
    def content(self):
        """Returns the contents of the entity."""
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
        """Returns entity content metadata."""
        return self.state.fields

    @property
    def links(self):
        """Returns a dictionary of related resources."""
        return self.state.links

    @property
    def name(self):
        """Returns the entity name."""
        return self.state.title

    @property
    def namespace(self):
        """The namespace this entity lives in.

        A ``Record`` with three keys: ``'owner'``, ``'app'``, and ``'sharing'``.
        """
        return namespace(owner = self._state.access['owner'],
                         app = self._state.access['app'],
                         sharing = self._state.access['sharing'])

    def read(self):
        """Reads the current state of the entity from the server."""
        response = self.get()
        results = self._load_state(response)
        return results

    def reload(self):
        """Reloads the entity."""
        self.post("_reload")
        return self

    @property
    def state(self):
        """Returns the entity's state record."""
        if self._state is None: self.refresh()
        return self._state

    def update(self, **kwargs):
        """Updates the entity with the arguments you provide.

        Note that you cannot update the ``name`` field of an Entity,
        due to a peculiarity of the REST API.

        Many of the fields in the REST API are not valid Python
        identifiers, which means you cannot pass them as keyword
        arguments. That is, Python will fail to parse the following::

            x.update(check-new=False, email.to='boris@utopia.net')

        However, you can always explicitly use a dictionary to pass
        such keys::

            x.update(**{'check-new': False, 'email.to': 'boris@utopia.net'})
        """
        # The peculiarity in question: the REST API creates a new
        # Entity if we pass name in the dictionary, instead of the
        # expected behavior of updating this Entity. Therefore we
        # check for 'name' in kwargs and throw an error if it is
        # there.
        if 'name' in kwargs:
            raise IllegalOperationException('Cannot update the name of an Entity via the REST API.')
        self.post(**kwargs)
        return self

class ReadOnlyCollection(Endpoint):
    """A read-only collection of entities in the Splunk instance.

    See the documentation for :class:`Collection` for most usage. The only
    difference is that it lacks :class:`ReadOnlyCollection` lacks
    :method:`create`, :method:`delete`
    """
    def __init__(self, service, path, item=Entity):
        Endpoint.__init__(self, service, path)
        self.item = item # Item accessor
        self.null_count = -1

    def __contains__(self, name):
        """Is there at least one entry called *name* in this collection?

        Makes a single roundtrip to the server, plus at most two more
        if autologin is enabled.
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
        entity given just the name. If there is a conflict and you
        pass just a name, it will raise a ``ValueError``. In that
        case, add the namespace as a second argument.

        This function makes a single roundtrip to the server, plus at
        most two additional round trips if autologin is enabled.

        :param key: The name to fetch, or a tuple (name, namespace)
        :return: An Entity object.
        :raises KeyError: if *key* does not exist.
        :raises ValueError: if no namespace is specified and *key* 
                            does not refer to a unique name.

        *Example*::

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
        if isinstance(key, tuple) and len(key) == 2:
            # x[a,b] is translated to x.__getitem__( (a,b) ), so we
            # have to extract values out.
            key, ns = key
        else:
            ns = self.service.namespace
        try:
            response = self.get(key, owner=ns.owner, app=ns.app)
            entries = self._load_list(response)
            if len(entries) > 1:
                raise AmbiguousReferenceException("Found multiple entities named '%s'; please specify a namespace." % key)
            elif len(entries) == 0:
                raise KeyError(key)
            else:
                return entries[0]
        except HTTPError as he:
            if he.status == 404: # No entity matching key and namespace.
                raise KeyError(key)
            else:
                raise

    def __iter__(self, **kwargs):
        """Iterate over the entities in the collection.

        :rtype: iterator over entities.

        Implemented to give Collection a listish interface. This
        function always makes a roundtrip to the server, plus at most
        two additional round trips if autologin is enabled.

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            saved_searches = c.saved_searches
            for entity in saved_searches:
                print "Saved search named %s" % entity.name
        """
        for item in self.iter(**kwargs):
            yield item

    def __len__(self):
        """Enable ``len(...)`` for ``Collection``s.

        Implemented for consistency with a listish interface. No
        further failure modes beyond those possible for any method on
        an Endpoint.

        This function always makes a round trip to the server, plus at
        most two additional round trips if autologin is enabled.

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

        :rtype: string
        :returns: an absolute path
        """
        # This has been factored out so that it can be easily
        # overloaded by Configurations, which has to switch its
        # entities' endpoints from its own properties/ to configs/.
        raw_path = urllib.unquote(state.links.alternate)
        if 'servicesNS/' in raw_path:
            return trailing(raw_path, 'servicesNS/', '/', '/')
        elif 'services/' in raw_path:
            return trailing(raw_path, 'services/')
        else:
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

    def contains(self, name):
        """**Deprecated**: Use the ``in`` operator instead.

        Indicates whether an entity name exists in the collection.

        Makes a single roundtrip to the server, plus at most two more
        if autologin is enabled.
        
        :param `name`: The entity name.
        :rtype: Boolean
        """
        return name in self

    def itemmeta(self):
        """Returns metadata for members of the collection.

        Makes a single roundtrip to the server, plus at most two more
        if autologin is enabled.

        :returns: a :class:`Record` containing the metadata.

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
                            'required': ['name'],
                            'wildcard': []}}
        """
        response = self.get("_new")
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return _parse_atom_metadata(content)

    def iter(self, offset=0, count=None, pagesize=None, **kwargs):
        """Iterate (possibly lazily) over the collection.

        This is equivalent to the :meth:`list` method, but
        it returns an iterator, and can load the entities a few at a
        time from the server (the number so loaded is controlled by
        the *pagesize* argument).

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
            logging.debug("pagesize=%d, fetched=%d, offset=%d, N=%d, kwargs=%s", pagesize, fetched, offset, N, kwargs)

    # kwargs: count, offset, search, sort_dir, sort_key, sort_mode
    def list(self, count=None, **kwargs):
        """Fetch a list of the entities in this collection.

        There is no laziness in this function. The entire collection
        is loaded at once and returned as a list. This function makes
        a single roundtrip to the server, plus at most two more if
        autologin is enabled. There is no caching: every call makes at
        least one round trip.

        :param `count`: The maximum number of items to return (optional).
        :param `offset`: The offset of the first item to return (optional).
        :param `search`: The search expression to filter responses (optional).
        :param `sort_dir`: The direction to sort returned items: *asc* or *desc*
                           (optional).
        :param `sort_key`: The field to use for sorting (optional).
        :param `sort_mode`: The collating sequence for sorting returned items:
                            *auto*, *alpha*, *alpha_case*, *num* (optional).
        :rtype: list
        """
        # response = self.get(count=count, **kwargs)
        # return self._load_list(response)
        return list(self.iter(count=count, **kwargs))

    def names(self, count=None, **kwargs):
        """Return a list of the names of all the entities in this collection.

        The entire list is loaded at once in a single roundtrip to the server,
        plus at most two more if autologin is enabled. There is no caching:
        every call makes at least one round trip.

        :param `count`: The maximum number of names to return (optional).
        :param `offset`: The offset of the first name to return (optional).
        :param `search`: The search expression to filter responses (optional).
        :param `sort_dir`: The direction to sort returned entites: *asc* or *desc*
                           (optional).
        :param `sort_key`: The field to use for sorting (optional).
        :param `sort_mode`: The collating sequence for sorting returned entities:
                            *auto*, *alpha*, *alpha_case*, *num* (optional).
        :rtype: list
        """
        return [ent.name for ent in self.iter(count=count, **kwargs)]

class Collection(ReadOnlyCollection):
    """A collection of entities in the Splunk instance.

    Splunk provides a number of different collections of distinct
    entity types: applications, saved searches, fired alerts, and a
    number of others. Each particular type is available separately
    from the Splunk instance, and the entities of that type are
    returned in a :class:`Collection`.

    :class:`Collection`'s interface does not quite match either
    ``list`` or ``dict`` in Python, since there are enough semantic
    mismatches with either to make its behavior surprising. A unique
    element in a :class:`Collection` is defined by a string giving its
    name plus a namespace object (though the namespace is optional if
    the name is unique).::

        import splunklib.client as client
        s = client.connect(...)
        c = s.saved_searches # c is a Collection
        m = c['my_search', client.namespace(owner='boris', app='natasha', sharing='user')]
        # Or if there is only one search visible named 'my_search'
        m = c['my_search']

    Similarly, ``"name" in c`` works as you expect (though you cannot
    currently pass a namespace to the ``in`` operator), as does
    ``len(c)``.

    However, as an aggregate, :class:`Collection` behaves more like a
    list. If you iterate over a :class:`Collection`, you get an
    iterator over the entities, not the names and namespaces::

        for entity in c:
            assert isinstance(entity, client.Entity)

    The :meth:`create` and :meth:`delete` methods create and delete
    entities in this collection. The access control list and other
    metadata of the collection is returned by the :meth:`itemmeta`
    method.

    :class:`Collection` does no caching. Each call makes at least one
    round trip to the server to fetch data.
    """
    def create(self, name, **params):
        """Create a new entity in this collection.

        This function makes either one or two roundtrips to the
        server, depending on the type of the entities in this
        collection, plus at most two more if autologin is enabled.

        :param name: The name of the entity to create.
        :type name: string
        :param namespace: A namespace, as created by the :func:`namespace`
                          function (optional). If you wish, you can set
                          ``owner``, ``app``, and ``sharing`` directly.
        :type namespace: :class:`Record` with keys ``'owner'``, ``'app'``, and
                         ``'sharing'``
        :param params: Additional entity-specific arguments (optional).
        :return: The new entity.
        :rtype: subclass of ``Entity``, chosen by ``self.item`` in ``Collection``

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            applications = s.apps
            new_app = applications.create("my_fake_app")
        """
        if not isinstance(name, basestring):
           raise InvalidNameException("%s is not a valid name for an entity." % name)
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
        else:
            entry = atom.entry
            state = _parse_atom_entry(entry)
            entity = self.item(
                self.service,
                self._entity_path(state),
                state=state)
            return entity

    def delete(self, name, **params):
        """Delete the entity *name* from the collection.

        :param name: The name of the entity to delete.
        :type name: string
        :rtype: the collection ``self``.

        This method is implemented for consistency with the REST
        interface's DELETE method.

        If there is no entity named *name* on the server, then throws
        a ``KeyError``. This function always makes a roundtrip to the
        server.

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
                raise KeyError("No such entity %s" % name)
            else:
                raise
        return self

class ConfigurationFile(Collection):
    """This class contains a single configuration, which is a collection of 
    stanzas."""
    # __init__'s arguments must match those of an Entity, not a
    # Collection, since it is being created as the elements of a
    # Configurations, which is a Collection subclass.
    def __init__(self, service, path, **kwargs):
        Collection.__init__(self, service, path, item=Stanza)
        self.name = kwargs['state']['title']

class Configurations(Collection):
    """Configuration files of this Splunk instance.

    Splunk's configuration is divided into files, and each file into
    stanzas. This collection is unusual in that the values in it are
    themselves collections: ``ConfigurationFile`` objects.
    """
    def __init__(self, service):
        Collection.__init__(self, service, PATH_PROPERTIES, item=ConfigurationFile)
        if self.service.namespace.owner == '-' or self.service.namespace.app == '-':
            raise ValueError("Configurations cannot have wildcards in namespace.")

    def __getitem__(self, key):
        # The configurations endpoint returns multiple entities when we ask for a single file.
        # This screws up the default implementation of __getitem__ from Collection, which thinks
        # that multiple entities means a name collision, so we have to override it here.
        try:
            response = self.get(key)
            return ConfigurationFile(self.service, PATH_CONF % key, state={'title': key})
        except HTTPError as he:
            if he.status == 404: # No entity matching key
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
            if he.status == 404: # No entity matching key
                return False
            else:
                raise

    def create(self, name, **kwargs):
        # This has to be overridden to handle the plumbing of creating
        # a ConfigurationFile (which is a Collection) instead of some
        # Entity.
        if not isinstance(name, basestring): 
            raise ValueError("Invalid name: %s" % repr(name))
        response = self.post(__conf=name, **kwargs)
        if response.status == 303:
            return self[name]
        elif response.status == 201:
            return ConfigurationFile(self.service, PATH_CONF % name, item=Stanza, state={'title': name})
        else:
            raise ValueError("Unexpected status code %s returned from creating a stanza" % response.status)

    def delete(self, key):
        try:
            super(Configurations, self).delete(key)
        except HTTPError as he:
            if he.status == 405:
                raise IllegalOperationException("Cannot delete configuration files from the REST API.")
            else:
                raise

    def _entity_path(self, state):
        # Overridden to make all the ConfigurationFile objects
        # returned refer to the configs/ path instead of the
        # properties/ path used by Configrations.
        return PATH_CONF % state['title']


class Stanza(Entity):
    """This class contains a single configuration stanza."""
    def submit(self, stanza):
        """Populates a stanza in the .conf file."""
        self.service.request(self.path, method="POST", body=stanza)
        return self

    def __len__(self):
        # The stanza endpoint returns all the keys at the same level in the XML as the eai information
        # and 'disabled', so to get an accurate length, we have to filter those out and have just
        # the stanza keys.
        return len([x for x in self._state.content.keys()
                    if not x.startswith('eai') and x != 'disabled'])

class AlertGroup(Entity):
    """This class contains an entity that represents a group of fired alerts 
    that can be accessed through the :meth:`alerts` property."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def __len__(self):
        return self.count

    @property
    def alerts(self):
        """Returns a collection of triggered alert instances."""
        return Collection(self.service, self.path)

    @property
    def count(self):
        """Returns the count of triggered alerts."""
        return int(self.content.get('triggered_alert_count', 0))

class Indexes(Collection):
    def default(self):
        index = self['_audit']
        return index['defaultDatabase']

    def delete(self, name):
        if self.service.splunk_version[0] >= 5:
            Collection.delete(self, name)
        else:
            raise IllegalOperationException("Deleting indexes via the REST API is "
                                            "not supported before Splunk version 5.")

class Index(Entity):
    """This class is an index class used to access specific operations."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def attach(self, host=None, source=None, sourcetype=None):
        """Opens a stream (a writable socket) for writing events to the index.

        :param `host`: The host value for events written to the stream.
        :param `source`: The source value for events written to the stream.
        :param `sourcetype`: The sourcetype value for events written to the 
                            stream.
        """
        args = { 'index': self.name }
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype
        path = UrlEncoded(PATH_RECEIVERS_STREAM + "?" + urllib.urlencode(args), skip_encode=True)

        # Since we need to stream to the index connection, we have to keep
        # the connection open and use the Splunk extension headers to note
        # the input mode
        sock = self.service.connect()
        headers = ["POST %s HTTP/1.1\r\n" % self.service._abspath(path),
                   "Host: %s:%s\r\n" % (self.service.host, int(self.service.port)),
                   "Accept-Encoding: identity\r\n",
                   "Authorization: %s\r\n" % self.service.token,
                   "X-Splunk-Input-Mode: Streaming\r\n",
                   "\r\n"]
        for h in headers:
            sock.write(h)
        return sock

    @contextlib.contextmanager
    def attached_socket(self, *args, **kwargs):
        """Open a raw socket in a with block to write data to Splunk.

        The arguments are identical to those for ``attach``. The socket is automatically
        closed at the end of the with block, even if an exception is raised in the block.

        :param `host`: The host value for events written to the stream.
        :param `source`: The source value for events written to the stream.
        :param `sourcetype`: The sourcetype value for events written to the

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            index = s.indexes['some_index']
            with index.attached_socket(sourcetype='test') as sock:
                sock.send('Test event\r\n')
        """
        try:
            sock = self.attach(*args, **kwargs)
            yield sock
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def clean(self, timeout=60):
        """Deletes the contents of the index.

        `clean` blocks until the index is empty, since it needs to restore
        values at the end.

        :param `timeout`: The time-out period for the operation, in seconds (the
                          default is 60).
        """
        self.refresh()
        tds = self['maxTotalDataSizeMB']
        ftp = self['frozenTimePeriodInSecs']
        try:
            self.update(maxTotalDataSizeMB=1, frozenTimePeriodInSecs=1)
            self.roll_hot_buckets()

            start = datetime.now()
            diff = timedelta(seconds=timeout)
            while self.content.totalEventCount != '0' and datetime.now() < start+diff:
                sleep(1)
                self.refresh()
        finally:
            # Restore original values
            self.update(maxTotalDataSizeMB=tds, frozenTimePeriodInSecs=ftp)
            if self.content.totalEventCount != '0':
                raise OperationError, "Cleaning index %s took longer than %s seconds; timing out." % \
                                      (self.name, timeout)
        return self

    def disable(self):
        """Disables this index."""
        # Starting in Ace, we have to do this with specific sharing,
        # unlike most other entities.
        self.post("disable")
        return self

    def enable(self):
        """Enables this index."""
        # Starting in Ace, we have to reenable this with a specific
        # sharing unlike most other entities.
        self.post("enable")
        return self

    def roll_hot_buckets(self):
        """Performs rolling hot buckets for this index."""
        self.post("roll-hot-buckets")
        return self

    def submit(self, event, host=None, source=None, sourcetype=None):
        """Submit a single event to the index using ``HTTP POST``.

        :param `host`: The host value of the event.
        :param `source`: The source value of the event.
        :param `sourcetype`: The sourcetype value of the event.
        """
        args = { 'index': self.name }
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype

        # The reason we use service.request directly rather than POST
        # is that we are not sending a POST request encoded using 
        # x-www-form-urlencoded (as we do not have a key=value body),
        # because we aren't really sending a "form".
        self.service.post(PATH_RECEIVERS_SIMPLE, body=event, **args)
        return self

    # kwargs: host, host_regex, host_segment, rename-source, sourcetype
    def upload(self, filename, **kwargs):
        """Uploads a file for immediate indexing. 
        
        .. Note: The file must be locally accessible from the server.
        
        :param `filename`: The name of the file to upload. The file can be 
                           a plain, compressed, or archived file.
        :param `kwargs`: Additional arguments (optional). For details, see the 
                         `POST data/inputs/oneshot 
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTinput#POST_data.2Finputs.2Foneshot>`_
                         endpoint in the Splunk REST API documentation.
        """
        kwargs['index'] = self.name
        path = 'data/inputs/oneshot'
        self.service.post(path, name=filename, **kwargs)
        return self

class Input(Entity):
    """This class represents a Splunk input. This class is the base for all 
    typed input classes and is also used when the client does not recognize an
    input kind."""
    def __init__(self, service, path, kind=None, **kwargs):
        # kind can be omitted (in which case it is inferred from the path)
        # Otherwise, valid values are the paths from data/inputs ("udp",
        # "monitor", "tcp/raw"), or two special cases: "tcp" (which is "tcp/raw")
        # and "splunktcp" (which is "tcp/cooked").
        Entity.__init__(self, service, path, **kwargs)
        if kind is None:
            path_segments = path.split('/')
            i = path_segments.index('inputs')
            self.kind = '/'.join(path_segments[i+1:-1])
            assert self.kind is not None
        else:
            self.kind = kind

        # Maintain compatibility with older kind labels
        if self.kind == 'tcp/raw':
            self.kind = 'tcp'
        if self.kind == 'tcp/cooked':
            self.kind = 'splunktcp'

# Inputs is a "kinded" collection, which is a heterogenous collection where
# each item is tagged with a kind, that provides a single merged view of all
# input kinds.
# UNDONE: contains needs to take a kind arg to disambiguate
class Inputs(Collection):
    """This class represents a collection of inputs. The collection is 
    heterogeneous and each member of the collection contains a *kind* property
    that indicates the specific type of input."""

    def __init__(self, service, kindmap=None):
        Collection.__init__(self, service, PATH_INPUTS, item=Input)

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            # Fetch a single kind
            kind, key = key
            try:
                response = self.get(self.kindpath(kind) + "/" + key)
                entries = self._load_list(response)
                if len(entries) > 1:
                    raise AmbiguousReferenceException("Found multiple inputs of kind %s named %s." % (kind, key))
                elif len(entries) == 0:
                    raise KeyError((kind,key))
                else:
                    return entries[0]
            except HTTPError as he:
                if he.status == 404: # No entity matching kind and key
                    raise KeyError((kind,key))
                else:
                    raise
        else:
            # Iterate over all the kinds looking for matches.
            kind = None
            candidate = None
            for kind in self.kinds:
                try:
                    response = self.get(kind + "/" + key)
                    entries = self._load_list(response)
                    if len(entries) > 1:
                        raise AmbiguousReferenceException("Found multiple inputs of kind %s named %s." % (kind, key))
                    elif len(entries) == 0:
                        pass
                    else:
                        if candidate is not None: # Already found at least one candidate
                            raise AmbiguousReferenceException("Found multiple inputs named %s, please specify a kind" % key)
                        candidate = entries[0]
                except HTTPError as he:
                    if he.status == 404:
                        pass # Just carry on to the next kind.
                    else:
                        raise
            if candidate is None:
                raise KeyError(key) # Never found a match
            else:
                return candidate

    def __contains__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            # If we specify a kind, this will shortcut properly
            try:
                self.__getitem__(key)
                return True
            except KeyError:
                return False
        else:
            # Without a kind, we want to minimize the number of round trips to the server, so we
            # reimplement some of the behavior of __getitem__ in order to be able to stop searching
            # on the first hit.
            for kind in self.kinds:
                try:
                    response = self.get(self.kindpath(kind) + "/" + key)
                    entries = self._load_list(response)
                    if len(entries) > 0:
                        return True
                    else:
                        pass
                except HTTPError as he:
                    if he.status == 404:
                        pass # Just carry on to the next kind.
                    else:
                        raise
            return False

    def create(self, kind, name, **kwargs):
        """Creates an input of a specific kind in this collection, with any 
        arguments you specify. 

        :param `kind`: The kind of input to create.
        :param `name`: The input name.
        :param `kwargs`: Additional entity-specific arguments (optional). For
                         valid arguments, see the POST requests for the
                         `/data/inputs/ 
                         <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTinput>`_ 
                         endpoints in the Splunk REST API documentation.
        :return: The new input.
        """
        kindpath = self.kindpath(kind)
        self.post(kindpath, name=name, **kwargs)
        path = _path(self.path + kindpath, name)
        return Input(self.service, path, kind)

    def delete(self, kind, name=None):
        """Removes an input from the collection.
        
        :param `name`: The name of the input to remove.
        """
        if name is None:
            name = kind
            self.service.delete(self[name].path)
        else:
            self.service.delete(self[kind, name].path)
        return self

    def itemmeta(self, kind):
        """Returns metadata for the members of a given kind."""
        response = self.get("%s/_new" % self._kindmap[kind])
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return _parse_atom_metadata(content)

    def _get_kind_list(self, subpath=[]):
        kinds = []
        response = self.get('/'.join(subpath))
        content = _load_atom_entries(response)
        for entry in content:
            this_subpath = subpath + [entry.title]
            if entry.title == 'all' or this_subpath == ['tcp','ssl']:
                continue
            elif 'create' in [x.rel for x in entry.link]:
                kinds.append('/'.join(subpath + [entry.title]))
            else:
                subkinds = self._get_kind_list(subpath + [entry.title])
                kinds.extend(subkinds)
        return kinds

    @property
    def kinds(self, subpath=[]):
        """Returns the list of input kinds that this collection contains."""
        return self._get_kind_list()

    def kindpath(self, kind):
        """Returns a path to the resources for a given input kind.

        :param `kind`: The input kind.
        """
        if kind in self.kinds:
            return kind
        # Special cases
        elif kind == 'tcp':
            return 'tcp/raw'
        elif kind == 'splunktcp':
            return 'tcp/cooked'
        else:
            raise ValueError("No such kind on server: %s" % kind)

    def list(self, *kinds, **kwargs):
        """Returns a list of inputs that belong to the collection. You can also
        filter by one or more input kinds.

        This function iterates over all possible inputs no matter what arguments you
        specify. Because the inputs collection is the union of all the inputs of each
        kind, we have to implement count, search, etc. at the Python level once all the
        data is fetched. There tend not to be vast numbers of inputs so this usually
        isn't a problem, but be aware of it.

        The exception is when you specify a single kind. Then it makes a single request
        with the usual semantics for count, offset, search, etc.

        :param `count`: The maximum number of items to return (optional).
        :param `offset`: The offset of the first item to return (optional).
        :param `search`: The search expression to filter responses (optional).
        :param `sort_dir`: The direction to sort returned items: *asc* or *desc*
                           (optional).
        :param `sort_key`: The field to use for sorting (optional).
        :param `sort_mode`: The collating sequence for sorting returned items:
                            *auto*, *alpha*, *alpha_case*, *num* (optional).
        :param `kinds`: The input kinds to return (optional).
        """
        if len(kinds) == 0:
            kinds = self.kinds
        if len(kinds) == 1:
            kind = kinds[0]
            logging.debug("Inputs.list taking short circuit branch for single kind.")
            path = self.kindpath(kind)
            logging.debug("Path for inputs: %s", path)
            try:
                response = self.service.get(path, **kwargs)
            except HTTPError, he:
                if he.status == 404: # No inputs of this kind
                    return []
            entities = []
            entries = _load_atom_entries(response)
            if entries is None:
                return [] # No inputs in a collection comes back with no feed or entry in the XML
            for entry in entries:
                state = _parse_atom_entry(entry)
                # Unquote the URL, since all URL encoded in the SDK
                # should be of type UrlEncoded, and all str should not
                # be URL encoded.
                path = urllib.unquote(state.links.alternate)
                entity = Input(self.service, path, kind, state=state)
                entities.append(entity)
            return entities

        search = kwargs.get('search', '*')

        entities = []
        for kind in kinds:
            response = None
            try:
                response = self.get(self.kindpath(kind), search=search)
            except HTTPError as e:
                if e.status == 404: 
                    continue # No inputs of this kind
                else: 
                    raise
                
            # UNDONE: Should use _load_list for the following, but need to
            # pass kind to the `item` method.
            entries = _load_atom_entries(response)
            if entries is None: continue # No inputs to process
            for entry in entries:
                state = _parse_atom_entry(entry)
                # Unquote the URL, since all URL encoded in the SDK
                # should be of type UrlEncoded, and all str should not
                # be URL encoded.
                path = urllib.unquote(state.links.alternate)
                entity = Input(self.service, path, kind, state=state)
                entities.append(entity)
        if 'offset' in kwargs:
            entities = entities[kwargs['offset']:]
        if 'count' in kwargs:
            entities = entities[:kwargs['count']]
        if kwargs.get('sort_mode', None) == 'alpha':
            sort_field = kwargs.get('sort_field', 'name')
            if sort_field == 'name':
                f = lambda x: x.name.lower()
            else:
                f = lambda x: x[sort_field].lower()
            entities = sorted(entities, key=f)
        if kwargs.get('sort_mode', None) == 'alpha_case':
            sort_field = kwargs.get('sort_field', 'name')
            if sort_field == 'name':
                f = lambda x: x.name
            else:
                f = lambda x: x[sort_field]
            entities = sorted(entities, key=f)
        if kwargs.get('sort_dir', 'asc') == 'desc':
            entities = list(reversed(entities))
        return entities

    def __iter__(self, **kwargs):
        for item in self.list(**kwargs):
            yield item

    def iter(self, **kwargs):
        for item in self.list(**kwargs):
            yield item

    def oneshot(self, path, **kwargs):
        try:
            self.post('oneshot', name=path, **kwargs)
        except HTTPError as he:
            if he.status == 400:
                raise OperationFailedException(he.message)
            else:
                raise


class Job(Entity):
    """This class represents a search job."""
    def __init__(self, service, sid, **kwargs):
        path = PATH_JOBS + sid
        Entity.__init__(self, service, path, skip_refresh=True, **kwargs)
        self.sid = sid
        self._is_ready = False

    # The Job entry record is returned at the root of the response
    def _load_atom_entry(self, response):
        return _load_atom(response).entry

    def cancel(self):
        """Stops the current search and deletes the result cache."""
        try:
            self.post("control", action="cancel")
        except HTTPError as he:
            if he.status == 404:
                # The job has already been cancelled, so
                # cancelling it twice is a nop.
                pass
            else:
                raise
        return self

    def disable_preview(self):
        """Disables preview for this job."""
        self.post("control", action="disablepreview")
        return self

    def enable_preview(self):
        """Enables preview for this job (although doing so might slow search
        considerably)."""
        self.post("control", action="enablepreview")
        return self

    def events(self, **kwargs):
        """Returns an InputStream IO handle for this job's events."""
        return self.get("events", **kwargs).body

    def finalize(self):
        """Stops the job and provides intermediate results available for 
        retrieval."""
        self.post("control", action="finalize")
        return self

    def is_done(self):
        """Has this job finished running on the server yet?

        :returns: boolean
        """
        if (not self.is_ready()):
            return False
        return self['isDone'] == '1'

    def is_ready(self):
        """Is this job queryable on the server yet?

        :returns: boolean
        """
        try:
            self.refresh()
            self._is_ready = True
            return self._is_ready
        except JobNotReadyException:
            self._is_ready = False
            return False

    @property
    def name(self):
        """Returns the name of the search job."""
        return self.sid

    def pause(self):
        """Suspends the current search."""
        self.post("control", action="pause")
        return self

    def refresh(self, state=None):
        """Refresh the state of this entity.

        If *state* is provided, load it as the new state for this
        entity. Otherwise, make a roundtrip to the server (by calling
        the :meth:`read` method of self) to fetch an updated state,
        plus at most two additional round trips if autologin is
        enabled.

        **Example**::

            import splunklib.client as client
            s = client.connect(...)
            search = s.jobs.create('search index=_internal | head 1')
            search.refresh()
        """
        if state is not None:
            self._state = state
        else:
            response = self.get()
            if response.status == 204:
                self._is_ready = False
                raise JobNotReadyException()
            else:
                self._is_ready = True
                raw_state = self._load_state(response)
                raw_state['links'] = dict([(k, urllib.unquote(v)) for k,v in raw_state['links'].iteritems()])
                self._state = raw_state
                return self

    def results(self, timeout=None, wait_time=1, **query_params):
        """Fetch search results as an InputStream IO handle.

        ``results`` returns a streaming handle over the raw data
        returned from the server. In order to get a nice, Pythonic
        iterator, pass the handle to ``results.ResultReader``, as in::

            import splunklib.client as client
            import splunklib.results as results
            s = client.connect(...)
            job = s.jobs.create("search * | head 5")
            r = results.ResultsReader(job.results())
            assert r.is_preview == False # The job is finished when we get here
            for kind, event in r:
                # events are returned as dicts with strings as values.
                print event 

        No results are available via this method until the job
        finishes. The method's behavior when called on an unfinished
        job is controlled by the *timeout* parameter. If *timeout* is
        ``None`` (the default), ``results`` will throw a
        ``ValueError`` immediately. If *timeout* is an integer,
        ``results`` will wait up to *timeout* seconds for the job to
        finish, and otherwise throw a ``ValueError``.

        With *timeout*``=None``, this method makes a single roundtrip
        to the server, plus at most two additional round trips if
        autologin is enabled. With *timeout* set to an integer, it
        polls repeatedly until it times out or the search is finished.

        :param timeout: Timeout in seconds, or ``None`` to fail immediately.
        :type timeout: ``float``
        :param wait_time: Minimum number of seconds to wait between polls.
        :type wait_time: ``float``
        :param query_params: Optional arguments for querying results. See the REST API documentation on `GET search/jobs/{search_id}/results  <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults>`_.
        :returns: A streaming handle over the response body.

        """
        if timeout is None:
            response = self.get("results", **query_params)
            if response.status == 204:
                raise ValueError("Job is still running; cannot return any events.")
            else:
                return response.body
        else:
            timeout = timedelta(seconds=timeout)
            start = datetime.now()
            while True:
                response = self.get("results", **query_params)
                if response.status == 204:
                    if datetime.now() - start < timeout:
                        sleep(wait_time)
                    else:
                        raise ValueError("Job is still running; cannot return any events.")
                else:
                    return response.body
                    

    def preview(self, **query_params):
        """Fetch an InputStream IO handle of preview search results.

        Unlike ``results``, which requires a job to be finished to
        return any results, ``preview`` returns whatever
        Splunk has so far, whether the job is running or not. The
        returned search results are the raw data from the server. Pass
        the handle returned to ``results.ResultsReader`` to get a
        nice, Pythonic iterator over objects, as in::

            import splunklib.client as client
            import splunklib.results as results
            s = client.connect(...)
            job = s.jobs.create("search * | head 5")
            r = results.ResultsReader(job.preview())
            if r.is_preview:
                print "Preview of a running search job."
            else:
                print "Job is finished. Results are final."
            for kind, event in r:
                assert kind == 'result'
                # events are returned as dicts with strings as values.
                print event 

        This method makes one roundtrip to the server, plus at most
        two more if autologin is turned on.

        :param query_params: Additional arguments to past to the REST endpoint. See see the `GET search/jobs/{search_id}/results_preview 
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fresults_preview>`_ 
                             endpoint in the REST API documentation.
        """
        response = self.get("results_preview", **query_params)
        if response.status == 204:
            raise ValueError("No events yet. Try again later.")
        else:
            return response.body

    def searchlog(self, **kwargs):
        """Returns an InputStream IO handle to the search log for this job.

        :param `kwargs`: Additional search log arguments (optional). For 
                         details, see the 
                         `GET search/jobs/{search_id}/search.log 
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fsearch.log>`_ 
                         endpoint in the REST API documentation.
        """
        return self.get("search.log", **kwargs).body

    def set_priority(self, value):
        """Sets this job's search priority in the range of 0-10.

        :param `value`: The search priority.
        """
        self.post('control', action="setpriority", priority=value)
        return self

    def summary(self, **kwargs):
        """Returns an InputStream IO handle to the job's summary.
        
        :param `kwargs`: Additional summary arguments (optional). For details, 
                         see the `GET search/jobs/{search_id}/summary 
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Fsummary>`_ 
                         endpoint in the REST API documentation.
        """
        return self.get("summary", **kwargs).body

    def timeline(self, **kwargs):
        """Returns an InputStream IO handle to the job's timeline results.

        :param `kwargs`: Additional timeline arguments (optional). For details, 
                         see the `GET search/jobs/{search_id}/timeline 
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#GET_search.2Fjobs.2F.7Bsearch_id.7D.2Ftimeline>`_ 
                         endpoint in the REST API documentation.
        """
        return self.get("timeline", **kwargs).body

    def touch(self):
        """Extends the expiration time of the search to the current time plus 
        the time-to-live value (now + ttl)."""
        self.post("control", action="touch")
        return self

    def set_ttl(self, value):
        """Set the job's time-to-live (ttl) value, which is the time before the 
        search job expires and is still available.

        :param `value`: The ttl value, in seconds.
        """
        self.post("control", action="setttl", ttl=value)
        return self

    def unpause(self):
        """Resumes the current search, if paused."""
        self.post("control", action="unpause")
        return self

class Jobs(Collection):
    """This class represents a collection of search jobs."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_JOBS, item=Job)
        # The count value to say list all the contents of this
        # Collection is 0, not -1 as it is on most.
        self.null_count = 0

    def _load_list(self, response):
        # Overridden because Job takes a sid instead of a path.
        entries = _load_atom_entries(response)
        if entries is None: return []
        entities = []
        for entry in entries:
            state = _parse_atom_entry(entry)
            entity = self.item(
                self.service,
                entry['content']['sid'],
                state=state)
            entities.append(entity)
        return entities

    def create(self, query, **kwargs):
        if kwargs.get("exec_mode", None) == "oneshot":
            raise TypeError("Cannot specify exec_mode=oneshot; use the oneshot method instead.")
        try:
            response = self.post(search=query, **kwargs)
        except HTTPError as he:
            if he.status == 400: # Bad request. Raise a TypeError with the reason.
                raise TypeError(he.message)
        sid = _load_sid(response)
        return Job(self.service, sid)

    def export(self, query, **params):
        """Run a search and immediately start streaming preview events.

        Returns an InputStream over the events. The InputStream
        streams an XML document from the server. The SDK provides
        ``results.ResultsReader`` to lazily parse this stream into
        usable Python objects. For example::

            import splunklib.client as client
            import splunklib.results as results
            s = client.connect(...)
            r = results.ResultsReader(s.jobs.export("search * | head 5"))
            assert r.is_preview == False # The job is finished when we get here
            for kind, event in r:
                assert kind == 'RESULT'
                # events are returned as dicts with strings as values.
                print event 

        ``export`` makes a single roundtrip to the server (as opposed
        to two for create followed by preview), plus at most two more
        if autologin is turned on.

        :raises ValueError: on invalid queries.

        :param query: Splunk search language query to run
        :type query: ``str``
        :param params: Additional arguments to export (see the `REST API docs <http://docs/Documentation/Splunk/4.3.2/RESTAPI/RESTsearch#search.2Fjobs.2Fexport>`_).
        :returns: InputStream over raw XML returned from the server.
        """
        if "exec_mode" in params:
            raise TypeError("Cannot specify an exec_mode to export.")
        try:
            return self.post(path_segment="export", search=query, **params).body
        except HTTPError as he:
            if he.status == 400:
                raise ValueError(str(he))
            else:
                raise

    def itemmeta(self):
        raise NotSupportedError()

    def oneshot(self, query, **params):
        """Run a search and directly return an InputStream IO handle over the results.

        The InputStream streams XML fragments from the server. The SDK
        provides ``results.ResultsReader`` to lazily parse this stream
        into usable Python objects. For example::

            import splunklib.client as client
            import splunklib.results as results
            s = client.connect(...)
            r = results.ResultsReader(s.jobs.oneshot("search * | head 5"))
            assert r.is_preview == False # The job is finished when we get here
            for kind, event in r:
                assert kind == 'RESULT'
                # events are returned as dicts with strings as values.
                print event 

        ``oneshot`` makes a single roundtrip to the server (as opposed
        to two for create followed by results), plus at most two more
        if autologin is turned on.

        :raises ValueError: on invalid queries.

        :param query: Splunk search language query to run
        :type query: ``str``
        :param params: Additional arguments to oneshot (see the `REST API docs <http://docs/Documentation/Splunk/latest/RESTAPI/RESTsearch#search.2Fjobs>`_).
        :returns: InputStream over raw XML returned from the server.
        """
        if "exec_mode" in params:
            raise TypeError("Cannot specify an exec_mode to oneshot.")
        try:
            return self.post(search=query, exec_mode="oneshot", **params).body
        except HTTPError as he:
            if he.status == 400:
                raise ValueError(str(he))
            else:
                raise
                
class Loggers(Collection):
    """This class represents a collection of service logging categories."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_LOGGER)

    def itemmeta(self):
        raise NotSupportedError

class Message(Entity):
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    @property
    def value(self):
        """Returns the message value."""
        return self[self.name]

class ModularInputKind(Entity):
    def __contains__(self, name):
        args = self.state.content['endpoints']['args']
        if name in args:
            return True
        else:
            return Entity.__contains__(self, name)

    def __getitem__(self, name):
        args = self.state.content['endpoint']['args']
        if name in args:
            return args['item']
        else:
            return Entity.__getitem__(self, name)

    @property
    def arguments(self):
        return self.state.content['endpoint']['args']

    def update(self, **kwargs):
        """Raises an error. Modular input kinds are read only."""
        raise IllegalOperationException("Modular input kinds cannot be updated via the REST API.")


class SavedSearch(Entity):
    """This class represents a saved search."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def acknowledge(self):
        """Acknowledges the suppression of alerts from this saved search and 
        resumes alerting."""
        self.post("acknowledge")
        return self

    @property
    def alert_count(self):
        """Return the number of alerts fired by this saved search.

        :return: The number of alerts fired by this saved search.
        :rtype: integer
        """
        return int(self._state.content.get('triggered_alert_count', 0))

    def dispatch(self, **kwargs):
        """Runs the saved search and returns the resulting search job.

        :param `kwargs`: Additional dispatch arguments (optional). For details, 
                         see the `POST saved/searches/{name}/dispatch
                         <http://docs.splunk.com/Documentation/Splunk/4.2.4/RESTAPI/RESTsearch#POST_saved.2Fsearches.2F.7Bname.7D.2Fdispatch>`_ 
                         endpoint in the REST API documentation.
        :return: The new search job.
        """
        response = self.post("dispatch", **kwargs)
        sid = _load_sid(response)
        return Job(self.service, sid)

    @property
    def fired_alerts(self):
        """Return a collection of AlertGroups corresponding to this saved search's alerts.

        If the search is not scheduled, raises ``IllegalOperationException``.

        :raises: IllegalOperationException
        :returns: Collection of AlertGroup entities.
        """
        if self['is_scheduled'] == '0':
            raise IllegalOperationException('Unscheduled saved searches have no alerts.')
        c = Collection(
            self.service,
            self.service._abspath(PATH_FIRED_ALERTS + self.name,
                                  owner=self.namespace.owner, app=self.namespace.app,
                                  sharing=self.namespace.sharing),
            item=AlertGroup)
        return c

    def history(self):
        """Returns a list of search jobs corresponding to this saved search.

        :return: A list of :class:`Job` objects.
        """
        response = self.get("history")
        entries = _load_atom_entries(response)
        if entries is None: return []
        jobs = []
        for entry in entries:
            job = Job(self.service, entry.title)
            jobs.append(job)
        return jobs

    def update(self, search=None, **kwargs):
        """Updates the saved search with any additional arguments.

        :param `search`: The search string of this saved search (optional).
        :param `kwargs`: Additional update arguments (optional). 
        """
        # Updates to a saved search *require* that the search string be 
        # passed, so we pass the current search string if a value wasn't
        # provided by the caller.
        if search is None: search = self.content.search
        Entity.update(self, search=search, **kwargs)
        return self

    def scheduled_times(self, earliest_time='now', latest_time='+1h'):
        """Returns the times when this search is scheduled to run.

        By default it returns the times in the next hour. For other
        periods, set *earliest_time* and *latest_time*. For example,
        for all times in the last day use ``earliest_time=-1d`` and
        ``latest_time=now``.
        """
        response = self.get("scheduled_times", 
                            earliest_time=earliest_time, 
                            latest_time=latest_time)
        data = self._load_atom_entry(response)
        rec = _parse_atom_entry(data)
        times = [datetime.fromtimestamp(int(t))
                 for t in rec.content.scheduled_times]
        return times

    def suppress(self, expiration):
        """Skip any scheduled runs of this search in the next *expiration* seconds."""
        self.post("suppress", suppressed="1", expiration=expiration)
        return self

    @property
    def suppressed(self):
        """The number of seconds that this search is blocked from running (possibly 0)."""
        r = self._run_method("suppress")
        if r.suppressed == "1":
            return int(r.expiration)
        else:
            return 0

    def unsuppress(self):
        """Cancel suppression and make this search run as scheduled."""
        self.post("suppress", suppressed="0", expiration="0")
        return self
        

class SavedSearches(Collection):
    """This class represents a collection of saved searches."""
    def __init__(self, service):
        Collection.__init__(
            self, service, PATH_SAVED_SEARCHES, item=SavedSearch)

    def create(self, name, search, **kwargs):
        return Collection.create(self, name, search=search, **kwargs)

class Settings(Entity):
    """This class represents configuration settings for a Splunk service."""
    def __init__(self, service, **kwargs):
        Entity.__init__(self, service, "server/settings", **kwargs)

    # Updates on the settings endpoint are POSTed to server/settings/settings.
    def update(self, **kwargs):
        self.service.post("server/settings/settings", **kwargs)
        return self

class User(Entity):
    @property
    def role_entities(self):
        """Return a list of entities representing all the roles assigned to this user."""
        return [self.service.roles[name] for name in self.content.roles]

# Splunk automatically lowercases new user names so we need to match that 
# behavior here to ensure that the subsequent member lookup works correctly.
class Users(Collection):
    """This class represents a Splunk user."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_USERS, item=User)

    def __getitem__(self, key):
        return Collection.__getitem__(self, key.lower())

    def __contains__(self, name):
        return Collection.__contains__(self, name.lower())

    def contains(self, name):
        """Deprecated: Use in operator instead.

        Check if there is a user *name* in this Splunk instance.
        """
        return Collection.__contains__(self, name.lower())

    def create(self, username, password, roles, **params):
        """Create a new user.

        This function makes two roundtrips to the server, plus at most
        two more if autologin is turned on.

        :param username: Username for the new user.
        :type username: string
        :param password: Password for the new user.
        :type password: string
        :param roles: A single role or list of roles for the user.
        :type roles: string or list of strings
        :param params: Optional parameters. See the `REST API documentation<http://docs/Documentation/Splunk/4.3.2/RESTAPI/RESTaccess#POST_authentication.2Fusers>`_.
        :return: A reference to the new user.
        :rtype: ``Entity``

        **Example**:

            import splunklib.client as client
            c = client.connect(...)
            users = c.users
            boris = users.create("boris", "securepassword", roles="user")
            hilda = users.create("hilda", "anotherpassword", roles=["user","power"])
        """
        if not isinstance(username, basestring): 
            raise ValueError("Invalid username: %s" % str(username))
        username = username.lower()
        self.post(name=username, password=password, roles=roles, **params)
        # splunkd doesn't return the user in the POST response body,
        # so we have to make a second round trip to fetch it.
        response = self.get(username)
        entry = _load_atom(response, XNAME_ENTRY).entry
        state = _parse_atom_entry(entry)
        entity = self.item(
            self.service,
            urllib.unquote(state.links.alternate),
            state=state)
        return entity

    def delete(self, name):
        return Collection.delete(self, name.lower())


class Role(Entity):
    def grant(self, *capabilities_to_grant):
        """Grant additional capabilities to this role.

        The capabilities are strings. You can get the complete list from
        Service.capabilities, or from the /authorization/capabilities
        endpoint in Splunk (or just look in splunkweb).

        **Example**::

            service = client.connect(...)
            role = service.roles['somerole']
            role.grant('change_own_password', 'search')

        :param capabilities_to_grant: Zero or more capabilities to grant this role.
        :return: The Role entity.
        """
        possible_capabilities = self.service.capabilities
        for capability in capabilities_to_grant:
            if capability not in possible_capabilities:
                raise NoSuchCapability(capability)
        self.refresh()
        new_capabilities = self['capabilities'] + list(capabilities_to_grant)
        self.post(capabilities=new_capabilities)
        return self

    def revoke(self, *capabilities_to_revoke):
        """Revoke zero or more capabilities from this role.

        The capabilities are strings. You can get the complete list from
        Service.capabilities, or from the /authorization/capabilities
        endpoint in Splunk (or just look in splunkweb).

        **Example**::

            service = client.connect(...)
            role = service.roles['somerole']
            role.revoke('change_own_password', 'search')

        :param capabilities_to_revoke: Zero or more capabilities to revoke from this role.
        :return: The Role entity
        """
        possible_capabilities = self.service.capabilities
        for capability in capabilities_to_revoke:
            if capability not in possible_capabilities:
                raise NoSuchCapability(capability)
        self.refresh()
        old_capabilities = self['capabilities']
        for capability in capabilities_to_revoke:
            if capability not in old_capabilities:
                raise ValueError("Role does not have capability %s" % capability)
        new_capabilities = []
        for c in old_capabilities:
            if c not in capabilities_to_revoke:
                new_capabilities.append(c)
        if new_capabilities == []:
            new_capabilities = '' # Empty lists don't get passed in the body, so we have to force an empty argument.
        self.post(capabilities=new_capabilities)
        return self



class Roles(Collection):
    """Roles in the Splunk instance."""
    def __init__(self, service):
        return Collection.__init__(self, service, PATH_ROLES, item=Role)

    def __getitem__(self, key):
        return Collection.__getitem__(self, key.lower())

    def __contains__(self, name):
        return Collection.__contains__(self, name.lower())

    def contains(self, name):
        """Deprecated: Use in operator instead.

        Check if there is a user *name* in this Splunk instance.
        """
        return Collection.__contains__(self, name.lower())

    def create(self, name, **params):
        """Create a new role.

        This function makes two roundtrips to the server, plus at most
        two more if autologin is turned on.

        :param name: Name for the role
        :type name: string
        :param params: Optional parameters. See the `REST API documentation<http://docs/Documentation/Splunk/4.3.2/RESTAPI/RESTaccess#POST_authorization.2Froles>`_.
        :return: A reference to the new role. 
        :rtype: ``Entity``

        **Example**::

            import splunklib.client as client
            c = client.connect(...)
            roles = c.roles
            paltry = roles.create("paltry", imported_roles="user", defaultApp="search")
        """
        if not isinstance(name, basestring): 
            raise ValueError("Invalid role name: %s" % str(name))
        name = name.lower()
        self.post(name=name, **params)
        # splunkd doesn't return the user in the POST response body,
        # so we have to make a second round trip to fetch it.
        response = self.get(name)
        entry = _load_atom(response, XNAME_ENTRY).entry
        state = _parse_atom_entry(entry)
        entity = self.item(
            self.service,
            urllib.unquote(state.links.alternate),
            state=state)
        return entity

    def delete(self, name):
        return Collection.delete(self, name.lower())


class OperationError(Exception): 
    """Raised for a failed operation, such as a time out."""
    pass

class NotSupportedError(Exception): 
    """Raised for operations that are not supported on a given object."""
    pass

class Application(Entity):
    """Binding for /apps/local/{name}."""
    @property
    def setupInfo(self):
        return self.content.get('eai:setup', None)

    def package(self):
        return self._run_method("package")

    def updateInfo(self):
        return self._run_method("update")

    


