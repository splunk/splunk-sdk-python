# Splunk Python SDK Changelog

## 0.8.6

### Breaking changes

* Added User.role_entities to return a list of the actual entity objects for the
  roles of a user. User.roles still returns a list of the role names.
* Job.enable_preview() and Job.disable_preview() have been removed, since the corresponding
  endpoints in Splunk's REST API are broken in Splunk 4.x.

	
## 0.8.5

### Features

* Expanded endpoint coverage. Now at parity with the Java SDK.
* Replaced ResultsReader with something shorter. Iteration now
  results either Message objects or dicts, and moved preview from
  iteration to a field.
* Entities can be fetched from collections by name plus namespace
  combinations (which are unique, unlike names alone). Fetching
  entries by name alone properly throws errors on name conflicts.
* Added a distinct AuthenticationError and optional autologin/autorelogin.
* Reduced roundtrips and listings with specific lookups in __getitem__ 
  and similar methods.
* Put in types and operations to make URL encoding of strings consistent.
* Pagination is implemented to stream search results a hunk at a time.
* Lots of docstrings expanded.
* Lots of small bugs fixed.

## 0.8.0 (beta)

### Features

* Improvements to entity state management
* Improvements to usability of entity collections
* Support for collection paging - collections now support the paging arguments:
  `count`, `offset`, `search`, `sort_dir`, `sort_key` and `sort_mode`. Note
  that `Inputs` and `Jobs` are not pageable collections and only support basic
  enumeration and iteration.
* Support for event types:
    - Added Service.event_types + units
    - Added examples/event_types.py
* Support for fired alerts:
    - Added Service.fired_alerts + units
    - Added examples/fired_alerts.py
* Support for saved searches:
    - Added Service.saved_searches + units
    - Added examples/saved_searches.py
* Sphinx based SDK docs and improved source code docstrings.
* Support for IPv6 - it is now possible to connect to a Splunk instance 
  listening on an IPv6 address.

### Breaking changes

#### Module name

The core module was renamed from `splunk` to `splunklib`. The Splunk product 
ships with an internal Python module named `splunk` and the name conflict 
with the SDK prevented installing the SDK into Splunk Python sandbox for use 
by Splunk extensions. This module name change enables the Python SDK to be 
installed on the Splunk server.

#### State caching

The client module was modified to enable Entity state caching which required
changes to the `Entity` interface and changes to the typical usage pattern. 
  
Previously, entity state values where retrieved with a call to `Entity.read`
which would issue a round-trip to the server and return a dictionary of values
corresponding to the entity `content` field and, in a similar way, a call to
`Entity.readmeta` would issue in a round-trip and return a dictionary
contianing entity metadata values. 
  
With the change to enable state caching, the entity is instantiated with a
copy of its entire state record, which can be accessed using a variety of
properties:

* `Entity.state` returns the entire state record
* `Entity.content` returns the content field of the state record
* `Entity.access` returns entity access metadata
* `Entity.fields` returns entity content metadata

`Entity.refresh` is a new method that issues a round-trip to the server
and updates the local, cached state record.

`Entity.read` still exists but has been changed slightly to return the
entire state record and not just the content field. Note that `read` does
not update the cached state record. The `read` method is basically a thin
wrapper over the corresponding HTTP GET that returns a parsed entity state
record instaed of the raw HTTP response.

The entity _callable_ returns the `content` field as before, but now returns
the value from the local state cache instead of issuing a round-trip as it
did before.

It is important to note that refreshing the local state cache is always 
explicit and always requires a call to `Entity.refresh`. So, for example
if you call `Entity.update` and then attempt to retrieve local values, you 
will not see the newly updated values, you will see the previously cached
values. The interface is designed to give the caller complete control of
when round-trips are issued and enable multiple updates to be made before
refreshing the entity.
  
The `update` and action methods are all designed to support a _fluent_ style
of programming, so for example you can write:

    entity.update(attr=value).refresh()

And

    entity.disable().refresh()
  
An important benefit and one of the primary motivations for this change is
that iterating a collection of entities now results in a single round-trip
to the server, because every entity collection member is initialized with
the result of the initial GET on the collection resource instead of requiring
N+1 round-trips (one for each entity + one for the collection), which was the
case in the previous model. This is a significant improvement for many
common scenarios.

#### Collections

The `Collection` interface was changed so that `Collection.list` and the 
corresponding collection callable return a list of member `Entity` objects
instead of a list of member entity names. This change was a result of user
feedback indicating that people expected to see eg: `service.apps()` return 
a list of apps and not a list of app names.

#### Naming context

Previously the binding context (`binding.Context`) and all tests & samples took
a single (optional) `namespace` argument that specified both the app and owner
names to use for the binding context. However, the underlying Splunk REST API
takes these as separate `app` and `owner` arguments and it turned out to be more
convenient to reflect these arguments directly in the SDK, so the binding 
context (and all samples & test) now take separate (and optional) `app` and
`owner` arguments instead of the prior `namespace` argument.

You can find a detailed description of Splunk namespaces in the Splunk REST
API reference under the section on accessing Splunk resources at:

* http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTresources

#### Misc. API

* Update all classes in the core library modules to use new-style classes
* Rename Job.setpriority to Job.set_priority
* Rename Job.setttl to Job.set_ttl

### Bug fixes

* Fix for GitHub Issues: 2, 10, 12, 15, 17, 18, 21
* Fix for incorrect handling of mixed case new user names (need to account for
  fact that Splunk automatically lowercases)
* Fix for Service.settings so that updates get sent to the correct endpoint
* Check name arg passed to Collection.create and raise ValueError if not
  a basestring
* Fix handling of resource names that are not valid URL segments by quoting the
  resource name when constructing its path

## 0.1.0a (preview)

* Fix a bug in the dashboard example
* Ramp up README with more info

## 0.1.0 (preview)

* Initial Python SDK release
