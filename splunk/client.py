# Copyright 2011 Splunk, Inc.
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

"""Client interface to the Splunk REST API."""

# A note on collections ..
#   * Entities have a kind, name & key. The kind is a tag that indicates the
#     "kind" of entity, name is a friendly name for the entity suitable for
#     display and key is a unique identifier for the Entity within its host
#     collection. In Splunk collections, name and key are frequently the same
#     but not always (eg: inputs).

from time import sleep
from urllib import urlencode, quote_plus
from urlparse import urlparse

from splunk.binding import Context, HTTPError
import splunk.data as data
from splunk.data import record

__all__ = [
    "connect",
    "Service"
]

PATH_APPS = "apps/local/"
PATH_CAPABILITIES = "authorization/capabilities/"
PATH_CONF = "configs/conf-%s/"
PATH_CONFS = "properties/"
PATH_INDEXES = "data/indexes/"
PATH_INPUTS = "data/inputs/"
PATH_JOBS = "search/jobs/"
PATH_LOGGER = "server/logger/"
PATH_MESSAGES = "messages/"
PATH_ROLES = "authentication/roles/"
PATH_STANZA = "configs/conf-%s/%s" # (file, stanza)
PATH_USERS = "authentication/users/"

XNAMEF_ATOM = "{http://www.w3.org/2005/Atom}%s"
XNAME_ENTRY = XNAMEF_ATOM % "entry"
XNAME_CONTENT = XNAMEF_ATOM % "content"

MATCH_ENTRY_CONTENT = "%s/%s/*" % (XNAME_ENTRY, XNAME_CONTENT)

# Constructs a path from the given conf & stanza
def _path_stanza(conf, stanza):
    return PATH_STANZA % (conf, quote_plus(stanza))

# kwargs: scheme, host, port, username, password, namespace
def connect(**kwargs):
    """Establishes an authenticated connection to the specified service."""
    return Service(**kwargs).login()

# Response utilities
def load(response, match=None):
    return data.load(response.body.read(), match)

class Service(Context):
    """The Splunk service."""
    def __init__(self, **kwargs):
        Context.__init__(self, **kwargs)

    @property
    def apps(self):
        """Return a collection of applications."""
        return Collection(self, PATH_APPS, "apps",
            item=lambda service, name: 
                Entity(service, PATH_APPS + name, name),
            ctor=lambda service, name, **kwargs:
                service.post(PATH_APPS, name=name, **kwargs),
            dtor=lambda service, name: service.delete(PATH_APPS + name))

    @property
    def confs(self):
        """Return a collection of configs."""
        return Collection(self, PATH_CONFS, "confs",
            item=lambda service, conf: 
                Collection(service, PATH_CONF % conf, conf,
                    item=lambda service, stanza:
                        Conf(service, _path_stanza(conf, stanza), stanza),
                    ctor=lambda service, stanza, **kwargs:
                        service.post(PATH_CONF % conf, name=stanza, **kwargs),
                    dtor=lambda service, stanza:
                        service.delete(_path_stanza(conf, stanza))))

    @property
    def capabilities(self):
        """Returns a list of all Splunk capabilities."""
        response = self.get(PATH_CAPABILITIES)
        return load(response, MATCH_ENTRY_CONTENT).capabilities

    @property
    def indexes(self):
        """Return a collection of indexes."""
        return Collection(self, PATH_INDEXES, "indexes",
            item=lambda service, name: 
                Index(service, name),
            ctor=lambda service, name, **kwargs:
                service.post(PATH_INDEXES, name=name, **kwargs))

    @property
    def info(self):
        """Returns server information."""
        response = self.get("server/info")
        return _filter_content(load(response, MATCH_ENTRY_CONTENT))

    @property
    def inputs(self):
        return Inputs(self)

    @property
    def jobs(self):
        """Returns a collection of current search jobs."""
        return Jobs(self)

    @property
    def loggers(self):
        """Returns a collection of logging categories."""
        return Collection(self, PATH_LOGGER, "loggers",
            item=lambda service, name: 
                Entity(service, PATH_LOGGER + name, name))

    @property
    def messages(self):
        """Returns a collection of service messages."""
        return Collection(self, PATH_MESSAGES, "messages",
            item=lambda service, name: Message(service, name),
            ctor=lambda service, name, **kwargs:
                service.post(PATH_MESSAGES, name=name, **kwargs), # value
            dtor=lambda service, name:
                service.delete(PATH_MESSAGES + name))

    # kwargs: enable_lookups, reload_macros, parse_only, output_mode
    def parse(self, query, **kwargs):
        """Test a search query through the parser."""
        return self.get("search/parser", q=query, **kwargs)

    def restart(self):
        """Restart the service."""
        return self.get("server/control/restart")

    @property
    def roles(self):
        return Collection(self, PATH_ROLES, "roles",
            item=lambda service, name: 
                Entity(service, PATH_ROLES + name, name),
            ctor=lambda service, name, **kwargs:
                service.post(PATH_ROLES, name=name, **kwargs),
            dtor=lambda service, name: service.delete(PATH_ROLES + name))

    @property
    def settings(self):
        """Return the server settings entity."""
        return Entity(self, "server/settings")

    @property
    def users(self):
        return Collection(self, PATH_USERS, "users",
            item=lambda service, name: 
                Entity(service, PATH_USERS + name, name),
            ctor=lambda service, name, **kwargs:
                service.post(PATH_USERS, name=name, **kwargs),
            dtor=lambda service, name: service.delete(PATH_USERS + name))

class Endpoint:
    """The base class for all client layer endpoints."""
    def __init__(self, service, path):
        self.service = service
        self.path = path if path.endswith('/') else path + '/'

    def get(self, relpath="", **kwargs):
        """A generic HTTP GET to the endpoint and optional relative path."""
        response = self.service.get("%s%s" % (self.path, relpath), **kwargs)
        return response

    def post(self, relpath="", **kwargs):
        """A generic HTTP POST to the endpoint and optional relative path."""
        response = self.service.post("%s%s" % (self.path, relpath), **kwargs)
        return response

class Collection(Endpoint):
    """A generic implementation of the Splunk collection protocol."""
    def __init__(self, service, path, name=None, 
                 item=None, ctor=None, dtor=None):
        Endpoint.__init__(self, service, path)
        if name is not None: self.name = name
        self.item = item # Item accessor
        self.ctor = ctor # Item constructor
        self.dtor = dtor # Item desteructor

    def __call__(self):
        return self.list()

    def __getitem__(self, key):
        if self.item is None: raise NotSupportedError
        if not self.contains(key): raise KeyError, key
        return self.item(self.service, key)

    def __iter__(self):
        # Don't invoke __getitem__ below, we don't need the extra round-trip
        # to validate that the key exists, because we just it from the list.
        for name in self.list(): yield self.item(self.service, name)

    def contains(self, name):
        return name in self.list()

    def create(self, name, **kwargs):
        if self.ctor is None: raise NotSupportedError
        self.ctor(self.service, name, **kwargs)
        return self[name]

    def delete(self, name):
        if self.dtor is None: raise NotSupportedError
        self.dtor(self.service, name)
        return self

    def itemmeta(self):
        """Returns metadata for members of the collection."""
        response = self.get("/_new")
        content = load(response, MATCH_ENTRY_CONTENT)
        return record({
            'eai:acl': content['eai:acl'],
            'eai:attributes': content['eai:attributes']
        })

    def list(self):
        """Returns a list of collection keys."""
        response = self.get(count=-1)
        entry = load(response).feed.get('entry', None)
        if entry is None: return []
        if not isinstance(entry, list): 
            entry = [entry]
        return [item.title for item in entry]

def _filter_content(content, *args):
    if len(args) > 0: # We have filter args
        result = record({})
        for key in args: result[key] = content[key]
    else:
        # Eliminate some noise by default
        result = content
        if result.has_key('eai:acl'):
            del result['eai:acl']
        if result.has_key('eai:attributes'):
            del result['eai:attributes']
        if result.has_key('type'):
            del result['type']
    return result

class Entity(Endpoint):
    """A generic implementation of the Splunk 'entity' protocol."""
    def __init__(self, service, path, name=None):
        Endpoint.__init__(self, service, path)
        if name is not None: self.name = name
        self.disable = lambda: self.post("disable")
        self.enable = lambda: self.post("enable")
        self.reload = lambda: self.post("_reload")

    def __call__(self):
        return self.read()

    def __getitem__(self, key):
        return self.read()[key]

    def __setitem__(self, key, value):
        self.update(**{ key: value })

    def read(self, *args):
        """Read and return the current entity value, optionally returning
           only the requested fields, if specified."""
        response = self.get()
        content = load(response, MATCH_ENTRY_CONTENT)
        return _filter_content(content, *args)

    def readmeta(self):
        """Return the entity's metadata."""
        return self.read('eai:acl', 'eai:attributes')

    def update(self, **kwargs):
        self.post(**kwargs)
        return self

class Conf(Entity):
    def submit(self, stanza):
        """Populates a stanza in the .conf file"""
        message = { 'method': "POST", 'body': stanza }
        response = self.service.request(self.path, message)

class Index(Entity):
    """Index class access to specific operations."""
    def __init__(self, service, name):
        Entity.__init__(self, service, PATH_INDEXES + name, name)
        self.roll_hot_buckets = lambda: self.post("roll-hot-buckets")

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

    def clean(self):
        """Delete the contents of the index."""
        saved = self.read('maxTotalDataSizeMB', 'frozenTimePeriodInSecs')
        self.update(maxTotalDataSizeMB=1, frozenTimePeriodInSecs=1)
        self.roll_hot_buckets()
        while True: # Wait until event count goes to zero
            sleep(1)
            if self['totalEventCount'] == '0': break
        self.update(**saved)

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
        response = self.service.request(path, message)

    # kwargs: host, host_regex, host_segment, rename-source, sourcetype
    def upload(self, filename, **kwargs):
        """Uploads a file to the index using the 'oneshot' input. The file
           must be accessible from the server."""
        kwargs['index'] = self.name
        path = 'data/inputs/oneshot'
        response = self.service.post(path, name=filename, **kwargs)

class Input(Entity):
    # kwargs: key, kind, name, path, links
    def __init__(self, service, **kwargs):
        Entity.__init__(self, service, kwargs['path'], kwargs['name'])
        self.key = kwargs['key']
        self.kind = kwargs['kind']

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

# Inputs is a kinded collection, which is a heterogenous collection where
# each item is tagged with a kind.
class Inputs(Endpoint):
    """A collection of Splunk inputs."""
    def __init__(self, service, kindmap=None):
        Endpoint.__init__(self, service, PATH_INPUTS)
        if kindmap is None: kindmap = INPUT_KINDMAP
        self._kindmap = kindmap
        self._infos = None
        self.refresh()
        
    # args: kind*
    def __call__(self, *args):
        return self.list(*args)

    def __getitem__(self, key):
        info = self._infos.get(key, None)
        if info is None: raise KeyError, key
        return Input(self.service, **info)

    def __iter__(self):
        # Don't invoke __getitem__ below, we don't need the extra round-trip
        # to validate that the key exists, because we just it from the list.
        for info in self._infos.itervalues(): 
            yield Input(self.service, **info)

    def contains(self, key):
        """Answers if the given key exists in the collection."""
        return key in self.list()

    def create(self, kind, name, **kwargs):
        """Creates an input of the given kind, with the given name & args."""
        response = self.post(self._kindmap[kind], name=name, **kwargs)
        return self.refresh()[self.itemkey(kind, name)]

    def delete(self, key):
        """Deletes the input with the given key."""
        response = self.service.delete(self._infos[key]['path'])
        self.refresh()
        return self

    def itemkey(self, kind, name):
        """Constructs a key from the given kind and item name."""
        if not kind in self._kindmap.keys(): 
            raise ValueError("Unknown kind '%s'" % kind)
        return "%s:%s" % (kind, name)

    def itemmeta(self, kind):
        """Returns metadata for members of the given kind."""
        response = self.get("%s/_new" % self._kindmap[kind])
        content = load(response, MATCH_ENTRY_CONTENT)
        return record({
            'eai:acl': content['eai:acl'],
            'eai:attributes': content['eai:attributes']
        })

    @property
    def kinds(self):
        """Returns the list of kinds that this collection may contain."""
        return self._kindmap.keys()

    def kindpath(self, kind):
        """Returns the path to resources of the given kind."""
        return self.path + self._kindmap[kind]

    # args: kind*
    def list(self, *args):
        """Returns a list of collection keys, optionally filtered by kind."""
        if len(args) == 0: return self._infos.keys()
        return [k for k, v in self._infos.iteritems() if v['kind'] in args]

    # Refreshes the 
    def refresh(self):
        """Refreshes the internal directory of entities and entity metadata."""
        self._infos = {}
        for kind in self.kinds:

            response = None
            try:
                response = self.service.get(self.kindpath(kind), count=-1)
            except HTTPError as e:
                if e.status == 404: 
                    continue # Nothing of this kind
                else: 
                    raise
                
            entry = load(response).feed.get('entry', None)
            if entry is None: continue
            if not isinstance(entry, list): entry = [entry]
            for item in entry:
                name = item.title
                key = self.itemkey(kind, name)
                path = urlparse(item.id).path
                links = dict([(link.rel, link.href) for link in item.link])
                self._infos[key] = {
                    'key': key,
                    'kind': kind,
                    'name': name,
                    'path': path,
                    'links': links,
                }
        return self

# The Splunk Job is not an enity, but we are able to make the interface look
# a lot like one.
class Job(Endpoint): 
    """Job class access to specific operations."""
    def __init__(self, service, sid):
        Endpoint.__init__(self, service, PATH_JOBS + sid)
        self.sid = sid

    def __call__(self):
        return self.read()

    def __getitem__(self, key):
        return self.read()[key]

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

    def pause(self):
        self.post("control", action="pause")
        return self

    def preview(self, **kwargs):
        return self.get("results_preview", **kwargs).body

    def read(self, *args):
        response = self.get()
        content = load(response).entry.content
        return _filter_content(content, *args)

    def results(self, **kwargs):
        return self.get("results", **kwargs).body

    def searchlog(self, **kwargs):
        return self.get("search.log", **kwargs).body

    def setpriority(self, value):
        self.post('control', action="setpriority", priority=value)
        return self

    def summary(self, **kwargs):
        return self.get("summary", **kwargs).body

    def timeline(self, **kwargs):
        return self.get("timeline", **kwargs).body

    def touch(self,):
        self.post("control", action="touch")
        return self

    def setttl(self, value):
        self.post("control", action="setttl", ttl=value)

    def unpause(self):
        self.post("control", action="unpause")
        return self

class Jobs(Collection):
    """A collection of search jobs."""
    def __init__(self, service):
        Collection.__init__(self, service, PATH_JOBS, "jobs",
            item=lambda service, sid: Job(service, sid))

    def create(self, query, **kwargs):
        response = self.post(search=query, **kwargs)

        if kwargs.get("exec_mode", None) == "oneshot":
            return response.body

        sid = load(response).response.sid
        return Job(self.service, sid)

    def list(self):
        response = self.get()
        entry = load(response, MATCH_ENTRY_CONTENT)
        if entry is None: return []
        if not isinstance(entry, list): entry = [entry]
        return [item.sid for item in entry]

class Message(Entity):
    def __init__(self, service, name):
        Entity.__init__(self, service, PATH_MESSAGES + name, name)

    @property
    def value(self):
        # The message value is contained in a entity property whose key is
        # the name of the message.
        return self[self.name]

class SplunkError(Exception): 
    pass

class NotSupportedError(Exception): 
    pass

