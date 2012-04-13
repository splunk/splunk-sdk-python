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

"""Client interface for the Splunk REST API."""

# UNDONE: Add Collection.refresh and list caching
# UNDONE: Resolve conflict between Collection.delete and name of REST method
# UNDONE: Add Endpoint.delete
# UNDONE: Add Entity.remove

from time import sleep
from urllib import urlencode, quote

from splunklib.binding import Context, HTTPError
import splunklib.data as data
from splunklib.data import record

__all__ = [
    "connect",
    "NotSupportedError",
    "OperationError",
    "Service"
]

PATH_APPS = "apps/local/"
PATH_CAPABILITIES = "authorization/capabilities/"
PATH_CONF = "configs/conf-%s/"
PATH_CONFS = "properties/"
PATH_EVENT_TYPES = "saved/eventtypes/"
PATH_FIRED_ALERTS = "alerts/fired_alerts/"
PATH_INDEXES = "data/indexes/"
PATH_INPUTS = "data/inputs/"
PATH_JOBS = "search/jobs/"
PATH_LOGGER = "server/logger/"
PATH_MESSAGES = "messages/"
PATH_ROLES = "authentication/roles/"
PATH_SAVED_SEARCHES = "saved/searches/"
PATH_STANZA = "configs/conf-%s/%s" # (file, stanza)
PATH_USERS = "authentication/users/"

XNAMEF_ATOM = "{http://www.w3.org/2005/Atom}%s"
XNAME_ENTRY = XNAMEF_ATOM % "entry"
XNAME_CONTENT = XNAMEF_ATOM % "content"

MATCH_ENTRY_CONTENT = "%s/%s/*" % (XNAME_ENTRY, XNAME_CONTENT)

# Filter the given state content record according to the given arg list.
def _filter_content(content, *args):
    if len(args) > 0:
        return record((k, content[k]) for k in args)
    return record((k, v) for k, v in content.iteritems()
        if k not in ['eai:acl', 'eai:attributes', 'type'])

# Construct a resource path from the given base path + resource name
def _path(base, name):
    if not base.endswith('/'): base = base + '/'
    return base + quote(name)

# Returns a path to the resource corresponding to the given conf name
def _path_conf(conf):
    return PATH_CONF % conf

# Load an atom record from the body of the given response
def _load_atom(response, match=None):
    return data.load(response.body.read(), match)

# Load an array of atom entries from the body of the given response
def _load_atom_entries(response):
    entries = _load_atom(response).feed.get('entry', None)
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

    econtent = entry.get('content', {})
    content = record((k, v) for k, v in econtent.iteritems()
        if k not in ['eai:acl', 'eai:attributes', 'type'])
    metadata = dict((k, econtent.get(k, None)) 
        for k in ['eai:acl', 'eai:attributes'])

    return record({
        'title': title,
        'links': links,
        'content': content,
        'metadata': metadata })

# kwargs: scheme, host, port, app, owner, username, password
def connect(**kwargs):
    """Establishes an authenticated connection to a Splunk :class:`Service`.

    :param `host`: host name (default `localhost`)
    :param `port`: port number (default 8089)
    :param `scheme`: scheme for accessing service (default `https`)
    :param `owner`: owner namespace (optional)
    :param `app`: app context (optional)
    :param `token`: session token (optional) - enables sharing session tokens
                    between multiple :class:`Service` istances
    :param `username`: username to login with
    :param `password`: password to login with
    :return: An initialized :class:`Service` instance
    """
    return Service(**kwargs).login()

class Service(Context):
    """Representation of a Splunk service at a given address (`host:port`)
    accessed using a given protocol "scheme" (`http` or `https`). 
    
    A service instance also captures an optional namespace context consisting 
    of an optional owner name (or "-" wildcard) and optional app name (or "-" 
    wildcard. In order to access :class:`Service` members the instance must
    be authenticated by presenting credentials using the :meth:`login` method 
    or by constructing the instance using the :func:`connect` function which 
    both creates and authenticates the instance.
    """

    def __init__(self, **kwargs):
        """Constructs a new :class:`Service` instance using the given 
        arguments.

        :param `host`: host name (default `localhost`)
        :param `port`: port number (default 8089)
        :param `scheme`: scheme for accessing service (default `https`)
        :param `owner`: owner namespace (optional)
        :param `app`: app context (optional)
        :param `token`: session token (optional)
        :param `username`: username to login with
        :param `password`: password to login with
        """
        Context.__init__(self, **kwargs)

    @property
    def apps(self):
        """Return a collection of applications."""
        return Collection(self, PATH_APPS)

    @property
    def confs(self):
        """Return a collection of configurations."""
        return Confs(self)

    @property
    def capabilities(self):
        """Returns a list of system capabilities."""
        response = self.get(PATH_CAPABILITIES)
        return _load_atom(response, MATCH_ENTRY_CONTENT).capabilities

    @property
    def event_types(self):
        """Returns a collection of saved event types."""
        return Collection(self, PATH_EVENT_TYPES)

    @property
    def fired_alerts(self):
        """Returns a collection of alerts that have been fired by the service.
        """
        return Collection(self, PATH_FIRED_ALERTS, item=AlertGroup)

    @property
    def indexes(self):
        """Return a collection of indexes."""
        return Collection(self, PATH_INDEXES, item=Index)

    @property
    def info(self):
        """Returns information about the sevice."""
        response = self.get("server/info")
        return _filter_content(_load_atom(response, MATCH_ENTRY_CONTENT))

    @property
    def inputs(self):
        """Returns a collection of configured inputs."""
        return Inputs(self)

    @property
    def jobs(self):
        """Returns a collection of current search jobs."""
        return Jobs(self)

    @property
    def loggers(self):
        """Returns a collection of service logging categories and their status.
        """
        return Collection(self, PATH_LOGGER)

    @property
    def messages(self):
        """Returns a collection of service messages."""
        return Collection(self, PATH_MESSAGES, item=Message)

    # kwargs: enable_lookups, reload_macros, parse_only, output_mode
    def parse(self, query, **kwargs):
        """Parse the given search query and return a semantic map of the search.

        :param query: the search query to parse
        :param kwargs: optional arguments to pass to the `search/parser` 
                       endpoint
        :return: semantic map of the parsed search query
        """
        return self.get("search/parser", q=query, **kwargs)

    def restart(self):
        """Restart the service. The service will be unavailable until it has
        successfully restarted.
        """
        return self.get("server/control/restart")

    @property
    def roles(self):
        """Returns a collection of user roles."""
        return Collection(self, PATH_ROLES)

    @property
    def saved_searches(self):
        """Returns a collection of saved searches."""
        return SavedSearches(self)

    @property
    def settings(self):
        """Returns configuration settings for the service."""
        return Settings(self)

    @property
    def users(self):
        """Returns a collection of users."""
        return Users(self)

class Endpoint(object):
    """The base class for all client layer endpoints."""
    def __init__(self, service, path):
        self.service = service
        self.path = path if path.endswith('/') else path + '/'

    def get(self, relpath="", **kwargs):
        """A generic HTTP GET to the endpoint and optional relative path."""
        return self.service.get("%s%s" % (self.path, relpath), **kwargs)

    def post(self, relpath="", **kwargs):
        """A generic HTTP POST to the endpoint and optional relative path."""
        return self.service.post("%s%s" % (self.path, relpath), **kwargs)

# kwargs: path, app, owner, sharing, state
class Entity(Endpoint):
    """A generic implementation of the Splunk entity protocol."""
    def __init__(self, service, path, **kwargs):
        Endpoint.__init__(self, service, path)
        self._state = None
        self.refresh(kwargs.get('state', None)) # "Prefresh"

    def __call__(self, *args):
        return self.content(*args)

    def __getitem__(self, key):
        return self.content[key]

    #
    # Given that update doesn't automatically refresh the cached local state,
    # this operation now violates the principle of least suprise, because it
    # allows you to do what appears to be a local assignment, which is then
    # not reflected in the value you see if you do a subsaquent __getitem__ 
    # without an explicit refresh.
    #
    # def __setitem__(self, key, value):
    #     self.update(**{ key: value })
    #

    # Load the Atom entry record from the given response - this is a method
    # because the "entry" record varies slightly by entity and this allows
    # for a subclass to override and handle any special cases.
    def _load_atom_entry(self, response):
        return _load_atom(response, XNAME_ENTRY).entry

    # Load the entity state record from the given response
    def _load_state(self, response):
        entry = self._load_atom_entry(response)
        return _parse_atom_entry(entry)

    def refresh(self, state=None):
        """Refresh the cached state of this entity, using either the given
           state record, or by calling `read` if no state record is provided."""
        self._state = state if state is not None else self.read()
        return self

    @property
    def content(self):
        """Return the contents of the entity."""
        return self.state.content

    def disable(self):
        self.post("disable")
        return self

    def enable(self):
        self.post("enable")
        return self

    @property
    def links(self):
        """Return a dictionary of related resources."""
        return self.state.links

    @property
    def metadata(self):
        """Return the entity metadata."""
        return self.state.metadata

    @property
    def name(self):
        """Return the entity name."""
        return self.state.title

    def read(self):
        """Read the current entity state from the server."""
        return self._load_state(self.get())

    def reload(self):
        self.post("_reload")
        return self

    @property
    def state(self):
        if self._state is None: self.refresh()
        return self._state

    def update(self, **kwargs):
        """Update the entity using the given kwargs."""
        self.post(**kwargs)
        return self

class Collection(Endpoint):
    """A generic implementation of the Splunk collection protocol."""
    def __init__(self, service, path, item=Entity):
        Endpoint.__init__(self, service, path)
        self.item = item # Item accessor

    def __call__(self, **kwargs):
        return self.list(**kwargs)

    def __contains__(self, name):
        return self.contains(name)

    def __getitem__(self, key):
        for item in self.list():
            if item.name == key: return item
        raise KeyError, key

    def __iter__(self):
        for item in self.list(): yield item

    # Load an entity list from the given response
    def _load_list(self, response):
        entries = _load_atom_entries(response)
        if entries is None: return []
        entities = []
        for entry in entries:
            state = _parse_atom_entry(entry)
            entity = self.item(
                self.service, 
                state.links.alternate,
                state=state)
            entities.append(entity)
        return entities

    def contains(self, name):
        """Answers if the given entity name exists in the collection."""
        for item in self.list():
            if item.name == name: return True
        return False

    def create(self, name, **kwargs):
        if not isinstance(name, basestring): 
            raise ValueError("Invalid argument: 'name'")
        self.post(name=name, **kwargs)
        return self[name] # UNDONE: Extra round-trip to retrieve entity

    def delete(self, name):
        self.service.delete(_path(self.path, name))
        return self

    def itemmeta(self):
        """Returns metadata for members of the collection."""
        response = self.get("_new")
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return {
            'eai:acl': content['eai:acl'],
            'eai:attributes': content['eai:attributes']
        }

    # kwargs: count, offset, search, sort_dir, sort_key, sort_mode
    def list(self, count=-1, **kwargs):
        response = self.get(count=count, **kwargs)
        return self._load_list(response)

class Conf(Collection):
    """A single config, which is a collection of stanzas."""
    def __init__(self, service, name):
        self.name = name
        Collection.__init__(self, service, _path_conf(name), item=Stanza)

class Confs(Collection):
    """A collection of configs."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_CONFS, 
            item=lambda service, path, **kwargs:
                Conf(service, kwargs['state'].title))

class Stanza(Entity):
    """A single config stanza."""
    def submit(self, stanza):
        """Populates a stanza in the .conf file."""
        message = { 'method': "POST", 'body': stanza }
        self.service.request(self.path, message)
        return self

class AlertGroup(Entity):
    """An entity that represents a group of fired alerts that can be accessed
       through the `alerts` property."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    @property
    def alerts(self):
        """Returns a collection of triggered alert instances."""
        return Collection(self.service, self.path)

    @property
    def count(self):
        """Returns the count of triggered alerts."""
        return int(self.content.triggered_alert_count)

class Index(Entity):
    """Index class access to specific operations."""
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def attach(self, host=None, source=None, sourcetype=None):
        """Opens a stream for writing events to the index."""
        args = { 'index': self.name }
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype
        path = "receivers/stream?%s" % urlencode(args)

        # Since we need to stream to the index connection, we have to keep
        # the connection open and use the Splunk extension headers to note
        # the input mode
        cn = self.service.connect()
        cn.write("POST %s HTTP/1.1\r\n" % self.service.fullpath(path))
        cn.write("Host: %s:%s\r\n" % (self.service.host, self.service.port))
        cn.write("Accept-Encoding: identity\r\n")
        cn.write("Authorization: %s\r\n" % self.service.token)
        cn.write("X-Splunk-Input-Mode: Streaming\r\n")
        cn.write("\r\n")
        return cn

    def clean(self, timeout=60):
        """Delete the contents of the index."""
        saved = self.refresh()('maxTotalDataSizeMB', 'frozenTimePeriodInSecs')
        self.update(maxTotalDataSizeMB=1, frozenTimePeriodInSecs=1)
        self.roll_hot_buckets()

        # Wait until the event count goes to zero
        count = 0
        while self.content.totalEventCount != '0' and count < timeout:
            sleep(1)
            count += 1
            self.refresh()

        self.update(**saved) # Restore original values
        if self.content.totalEventCount != '0':
            raise OperationError, "Operation timed out."
        return self

    def roll_hot_buckets(self):
        self.post("roll-hot-buckets")
        return self

    def submit(self, event, host=None, source=None, sourcetype=None):
        """Submits an event to the index via HTTP POST."""
        args = { 'index': self.name }
        if host is not None: args['host'] = host
        if source is not None: args['source'] = source
        if sourcetype is not None: args['sourcetype'] = sourcetype

        # The reason we use service.request directly rather than POST
        # is that we are not sending a POST request encoded using 
        # x-www-form-urlencoded (as we do not have a key=value body),
        # because we aren't really sending a "form".
        path = "receivers/simple?%s" % urlencode(args)
        message = { 'method': "POST", 'body': event }
        self.service.request(path, message)
        return self

    # kwargs: host, host_regex, host_segment, rename-source, sourcetype
    def upload(self, filename, **kwargs):
        """Uploads a file to the index using the 'oneshot' input. The file
           must be accessible from the server."""
        kwargs['index'] = self.name
        path = 'data/inputs/oneshot'
        self.service.post(path, name=filename, **kwargs)
        return self

class Input(Entity):
    # kwargs: path, kind
    def __init__(self, service, path, kind, **kwargs):
        Entity.__init__(self, service, path, **kwargs)
        self.kind = kind

# Directory of known input kinds that maps from input kind to path relative 
# to data/inputs, eg: inputs of kind 'splunktcp' map to a relative path
# of 'tcp/cooked' and therefore an endpoint path of 'data/inputs/tcp/cooked'.
INPUT_KINDMAP = {
    'ad': "ad",
    'monitor': "monitor",
    'registry': "registry",
    'script': "script",
    'tcp': "tcp/raw",
    'splunktcp': "tcp/cooked",
    'udp': "udp",
    'win-event-log-collections': "win-event-log-collections", 
    'win-perfmon': "win-perfmon",
    'win-wmi-collections': "win-wmi-collections"
}

# Inputs is a "kinded" collection, which is a heterogenous collection where
# each item is tagged with a kind, that provides a single merged view of all
# input kinds.
# UNDONE: contains needs to take a kind arg to disambiguate
class Inputs(Collection):
    """A merged view of all Splunk inputs."""
    def __init__(self, service, kindmap=None):
        Collection.__init__(self, service, PATH_INPUTS)
        self._kindmap = kindmap if kindmap is not None else INPUT_KINDMAP
        
    # args: kind*
    def __call__(self, *args):
        return self.list(*args)

    def create(self, kind, name, **kwargs):
        """Creates an input of the given kind, with the given name & args."""
        kindpath = self.kindpath(kind)
        self.service.post(kindpath, name=name, **kwargs)
        return Input(self.service, _path(kindpath, name), kind)

    def delete(self, name):
        """Deletes the input with the given name."""
        self.service.delete(self[name].path) # UNDONE: Should be item.remove()
        return self

    def itemmeta(self, kind):
        """Returns metadata for members of the given kind."""
        response = self.get("%s/_new" % self._kindmap[kind])
        content = _load_atom(response, MATCH_ENTRY_CONTENT)
        return {
            'eai:acl': content['eai:acl'],
            'eai:attributes': content['eai:attributes']
        }

    @property
    def kinds(self):
        """Returns the list of kinds that this collection may contain."""
        return self._kindmap.keys()

    def kindpath(self, kind):
        """Returns the path to resources of the given kind."""
        return self.path + self._kindmap[kind]

    # args: kind*
    def list(self, *args):
        """Returns a list of Input entities, optionally filtered by kind."""
        kinds = args if len(args) > 0 else self._kindmap.keys()

        entities = []
        for kind in kinds:
            response = None
            try:
                response = self.service.get(self.kindpath(kind), count=-1)
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
                path = state.links.alternate
                entity = Input(self.service, path, kind, state=state)
                entities.append(entity)

        return entities

class Job(Entity): 
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    # The Job entry record is returned at the root of the response
    def _load_atom_entry(self, response):
        return _load_atom(response).entry

    def cancel(self):
        self.post("control", action="cancel")
        return self

    def disable_preview(self):
        self.post("control", action="disablepreview")
        return self

    def events(self, **kwargs):
        return self.get("events", **kwargs).body

    def enable_preview(self):
        self.post("control", action="enablepreview")
        return self

    def finalize(self):
        self.post("control", action="finalize")
        return self

    @property
    def name(self):
        return self.sid

    def pause(self):
        self.post("control", action="pause")
        return self

    def preview(self, **kwargs):
        return self.get("results_preview", **kwargs).body

    def read(self):
        # If the search job is newly created, it is possible that we will 
        # get 204s (No Content) until the job is ready to respond.
        count = 0
        while count < 10:
            response = self.get()
            if response.status == 204: 
                sleep(1) 
                count += 1
                continue
            return self._load_state(response)
        raise OperationError, "Operation timed out."

    def results(self, **kwargs):
        return self.get("results", **kwargs).body

    def searchlog(self, **kwargs):
        return self.get("search.log", **kwargs).body

    def set_priority(self, value):
        self.post('control', action="setpriority", priority=value)
        return self

    @property
    def sid(self):
        return self.content.get('sid', None)

    def summary(self, **kwargs):
        return self.get("summary", **kwargs).body

    def timeline(self, **kwargs):
        return self.get("timeline", **kwargs).body

    def touch(self):
        self.post("control", action="touch")
        return self

    def set_ttl(self, value):
        self.post("control", action="setttl", ttl=value)
        return self

    def unpause(self):
        self.post("control", action="unpause")
        return self

class Jobs(Collection):
    """A collection of search jobs."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_JOBS, item=Job)

    def create(self, query, **kwargs):
        response = self.post(search=query, **kwargs)
        if kwargs.get("exec_mode", None) == "oneshot":
            return response.body
        sid = _load_sid(response)
        return Job(self.service, PATH_JOBS + sid)

    def list(self, count=0, **kwargs):
        return Collection.list(self, count, **kwargs)

class Message(Entity):
    def __init__(self, service, name, **kwargs):
        Entity.__init__(self, service, _path(PATH_MESSAGES, name), **kwargs)

    @property
    def value(self):
        # The message value is contained in a entity property whose key is
        # the name of the message.
        return self[self.name]

class SavedSearch(Entity):
    def __init__(self, service, path, **kwargs):
        Entity.__init__(self, service, path, **kwargs)

    def acknowledge(self):
        self.post("acknowledge")
        return self

    def dispatch(self, **kwargs):
        response = self.post("dispatch", **kwargs)
        sid = _load_sid(response)
        return Job(self.service, PATH_JOBS + sid)

    def history(self):
        response = self.get("history")
        entries = _load_atom_entries(response)
        if entries is None: return []
        jobs = []
        for entry in entries:
            job = Job(self.service, PATH_JOBS + entry.title)
            jobs.append(job)
        return jobs

    def update(self, search=None, **kwargs):
        # Updates to a saved search *require* that the search string be 
        # passed, so we pass the current search string if a value wasn't
        # provided by the caller.
        if search is None: search = self.content.search
        Entity.update(self, search=search, **kwargs)
        return self

class SavedSearches(Collection):
    def __init__(self, service):
        Collection.__init__(
            self, service, PATH_SAVED_SEARCHES, item=SavedSearch)

    def create(self, name, search, **kwargs):
        return Collection.create(self, name, search=search, **kwargs)

class Settings(Entity):
    def __init__(self, service, **kwargs):
        Entity.__init__(self, service, "server/settings", **kwargs)

    # Updates on the settings endpoint are POSTed to server/settings/settings.
    def update(self, **kwargs):
        self.service.post("server/settings/settings", **kwargs)
        return self

# Splunk automatically lowercases new user names so we need to match that 
# behavior here to ensure that the subsequent member lookup works correctly.
class Users(Collection):
    def __init__(self, service):
        Collection.__init__(self, service, PATH_USERS)

    def __getitem__(self, key):
        return Collection.__getitem__(self, key.lower())

    def contains(self, name):
        return Collection.contains(self, name.lower())

    def create(self, name, **kwargs):
        return Collection.create(self, name.lower(), **kwargs)

    def delete(self, name):
        return Collection.delete(self, name.lower())

class OperationError(Exception): 
    pass

class NotSupportedError(Exception): 
    pass

