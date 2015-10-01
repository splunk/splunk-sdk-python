# Splunk SDK for Python Changelog

## Version 1.5.0

### New features and APIs

* Added support for the new experimental Search Command Protocol v2, for Splunk 6.3+.

  Opt-in by setting `chunked = true` in commands.conf. See `examples/searchcommands_app/package/default/commands-scpv2.conf`.

* Added support for invoking external search command processes.

  See `examples/searchcommands_app/package/bin/pypygeneratext.py`.

* Added a new search command type: EventingCommand is the base class for commands that filter events arriving at a
  search head from one or more search peers.

  See `examples/searchcommands_app/package/bin/filter.py`.

* Added `splunklib` logger so that command loggers can be configured independently of the `splunklib.searchcommands`
  module.

  See `examples/searchcommands_app/package/default/logger.conf` for guidance on logging configuration.

* Added `splunklib.searchcommands.validators.Match` class for verifying that an option value matches a regular
  expression pattern.

### Bug fixes

* GitHub issue 88: `splunklib.modularinput`, `<done/>` written even when `done=False`.

* GitHub issue 115: `splunklib.searchcommands.splunk_csv.dict_reader` raises `KeyError` when `supports_multivalues = True`.

* GitHub issue 119: `None` returned in `_load_atom_entries`.

* Various other bug fixes/improvements for Search Command Protocol v1.

* Various bug fixes/improvements to the full splunklib test suite.

## Version 1.4.0

### New features and APIs

* Added support for cookie-based authentication, for Splunk 6.2+.

* Added support for installing as a Python egg.

* Added a convenience `Service.job()` method to get a `Job` by its sid.

### Bug fixes

* Restored support for Python 2.6 (GitHub issues #96 & #114).

* Fix `SearchCommands` decorators and `Validator` classes (Github issue #113).

* Fix `SearchCommands` bug iterating over `None` in `dict_reader.fieldnames` (Github issue #110).

* Fixed JSON parsing errors (GitHub issue #100).

* Retain the `type` property when parsing Atom feeds (GitHub issue #92).

* Update non-namespaced server paths with a `/services/` prefix. Fixes a bug where setting the `owner` and/or `app` on a `Service` could produce 403 errors on some REST API endpoints.

* Modular input `Argument.title` is now written correctly.

* `Client.connect` will now always return a `Service` instance, even if user credentials are invalid.

* Update the `saved_search/saved_search.py` example to handle saved searches with names containing characters that must be URL encoded (ex: `"Top 5 sourcetypes"`).

### Minor Changes

* Update modular input examples with readable titles.

* Improvements to `splunklib.searchcommands` tests.

* Various docstring and code style corrections.

* Updated some tests to pass on Splunk 6.2+.

## Version 1.3.1

### Bug fixes

* Hot fix to `binding.py` to work with Python 2.7.9, which introduced SSL certificate validation by default as outlined in [PEP 476](https://www.python.org/dev/peps/pep-0476).
* Update `async`, `handler_proxy`, and `handler_urllib2` examples to work with Python 2.7.9 by disabling SSL certificate validation by default.

## Version 1.3.0

### New features and APIs

* Added support for Storage Passwords. 

* Added a script (GenerateHelloCommand) to the searchcommand_app to generate a custom search command.

* Added a human readable argument titles to modular input examples.

* Renamed the searchcommand `csv` module to `splunk_csv`.

### Bug fixes

* Now entities that contain slashes in their name can be created, accessed and deleted correctly.

* Fixed a perfomance issue with connecting to Splunk on Windows.

* Improved the `service.restart()` function.

## Version 1.2.3

### New features and APIs

* Improved error handling in custom search commands

  SearchCommand.process now catches all exceptions and

  1. Writes an error message for display in the Splunk UI.

     The error message is the text of the exception. This is new behavior.

  2. Logs a traceback to SearchCommand.logger. This is old behavior.

* Made ResponseReader more streamlike, so that it can be wrapped in an 
  io.BufferedReader to realize a significant performance gain.

  *Example usage*

  ```
  import io
  ...
  response = job.results(count=maxRecords, offset=self._offset)
  resultsList = results.ResultsReader(io.BufferedReader(response)) 
  ```

### Bug fixes

1. The results reader now catches SyntaxError exceptions instead of
   `xml.etree.ElementTree.ParseError` exceptions. `ParseError` wasn't
   introduced until Python 2.7. This masked the root cause of errors
   data errors in result elements.

2. When writing a ReportingCommand you no longer need to include a map method.
 
## Version 1.2.2

### Bug fixes

1. Addressed a problem with autologin and added test coverage for the use case.

   See `ServiceTestCase.test_autologin` in tests/test_service.py.

## Version 1.2.1

### New features and APIs

* Added features for building custom search commands in Python

  1. Access Splunk Search Results Info.

     See the `SearchCommand.search_results_info` property.

  2. Communicate with Splunk.

     See the `SearchCommand.service` property.

  3. Control logging and view command configuration settings from the Splunk
     command line

     + The `logging_configuration` option lets you pick an alternative logging
       configuration file for a command invocation.

     + The `logging_level` option lets you set the logging level for a command
       invocation.

     + The `show_configuration` option writes command configuration settings
       to the Splunk Job Inspector.

  4. Get a more complete picture of what's happening when an error occurs

     Command error messages now include a full stack trace.

  5. Enable the Splunk Search Assistant to display command help.

     See `examples/searchcommands_app/default/searchbnf.conf`

  6. Write messages for display by the job inspector.

     See `SearchCommand.messages`.

* Added a feature for building modular inputs.

  1. Communicate with Splunk.

     See the `Script.service` property.

### Bug fixes

* When running `setup.py dist` without running `setup.py build`, there is no
  longer an `No such file or directory` error on the command line, and the
  command behaves as expected.

* When setting the sourcetype of a modular input event, events are indexed
  properly.

  Previously Splunk would encounter an error and skip them.

### Quality improvements

* Better code documentation and unit test coverage.

## Version 1.2

### New features and APIs

* Added support for building custom search commands in Python using the Splunk
  SDK for Python.

### Bug fix

* When running `setup.py dist` without running `setup.py build`, there is no
  longer an `No such file or directory` error on the command line, and the
  command behaves as expected.

* When setting the sourcetype of a modular input event, events are indexed properly.
  Previously Splunk would encounter an error and skip them.

### Breaking changes

* If modular inputs were not being indexed by Splunk because a sourcetype was set
  (and the SDK was not handling them correctly), they will be indexed upon updating
  to this version of the SDK.

### Minor changes

* Docstring corrections in the modular input examples.

* A minor docstring correction in `splunklib/modularinput/event_writer.py`.

## Version 1.1

### New features and APIs

* Added support for building modular input scripts in Python using the Splunk
  SDK for Python.

### Minor additions

* Added 2 modular input examples: `Github forks` and `random numbers`.

* Added a `dist` command to `setup.py`. Running `setup.py dist` will generate
  2 `.spl` files for the new modular input example apps.

* `client.py` in  the `splunklib` module will now restart Splunk via an HTTP
  post request instead of an HTTP get request.

* `.gitignore` has been updated to ignore `local` and `metadata` subdirectories
for any examples.

## Version 1.0

### New features and APIs

* An `AuthenticationError` exception has been added.
  This exception is a subclass of `HTTPError`, so existing code that expects 
  HTTP 401 (Unauthorized) will continue to work.
 
* An `"autologin"` argument has been added to the `splunklib.client.connect` and
  `splunklib.binding.connect` functions. When set to true, Splunk automatically 
  tries to log in again if the session terminates.
 
* The `is_ready` and `is_done` methods have been added to the `Job` class to 
  improve the verification of a job's completion status.
 
* Modular inputs have been added (requires Splunk 5.0+).
 
* The `Jobs.export` method has been added, enabling you to run export searches.
 
* The `Service.restart` method now takes a `"timeout"` argument. If a timeout 
  period is specified, the function blocks until splunkd has restarted or the 
  timeout period has passed. Otherwise, if a timeout period has not been 
  specified, the function returns immediately and you must check whether splunkd
  has restarted yourself.
 
* The `Collections.__getitem__` method can fetch items from collections with an 
  explicit namespace. This example shows how to retrieve a saved search for a 
  specific namespace:

        from splunklib.binding import namespace
        ns = client.namespace(owner='nobody', app='search')
        result = service.saved_searches['Top five sourcetypes', ns]       

* The `SavedSearch` class has been extended by adding the following:
    - Properties: `alert_count`, `fired_alerts`, `scheduled_times`, `suppressed`
    - Methods: `suppress`, `unsuppress`
 
* The `Index.attached_socket` method has been added. This method can be used 
  inside a `with` block to submit multiple events to an index, which is a more 
  idiomatic style than using the existing `Index.attach` method.
 
* The `Indexes.get_default` method has been added for returnings the name of the
  default index.
 
* The `Service.search` method has been added as a shortcut for creating a search
  job.
 
* The `User.role_entities` convenience method has been added for returning a 
  list of role entities of a user.
 
* The `Role` class has been added, including the `grant` and `revoke` 
  convenience methods for adding and removing capabilities from a role.
 
* The `Application.package` and `Application.updateInfo` methods have been 
  added.
 

### Breaking changes

* `Job` objects are no longer guaranteed to be ready for querying.
  Client code should call the `Job.is_ready` method to determine when it is safe
  to access properties on the job.
  
* The `Jobs.create` method can no longer be used to create a oneshot search
  (with `"exec_mode=oneshot"`). Use the `Jobs.oneshot` method instead.
  
* The `ResultsReader` interface has changed completely, including:
    - The `read` method has been removed and you must iterate over the 
      `ResultsReader` object directly.
    - Results from the iteration are either `dict`s or instances of 
      `results.Message`.
      
* All `contains` methods on collections have been removed.
  Use Python's `in` operator instead. For example: 
  
        # correct usage
        'search' in service.apps
       
        # incorrect usage
        service.apps.contains('search')
    
* The `Collections.__getitem__` method throws `AmbiguousReferenceException` if
  there are multiple entities that have the specified entity name in
  the current namespace.
  
* The order of arguments in the `Inputs.create` method has changed. The `name`
  argument is now first, to be consistent with all other collections and all 
  other operations on `Inputs`.
  
* The `ConfFile` class has been renamed to `ConfigurationFile`.

* The `Confs` class has been renamed to `Configurations`.
  
* Namespace handling has changed and any code that depends on namespace handling
  in detail may break.
  
* Calling the `Job.cancel` method on a job that has already been cancelled no 
  longer has any effect.
  
* The `Stanza.submit` method now takes a `dict` instead of a raw string.


### Bug fixes and miscellaneous changes

* Collection listings are optionally paginated.
 
* Connecting with a pre-existing session token works whether the token begins 
  with 'Splunk ' or not; the SDK handles either case correctly.
  
* Documentation has been improved and expanded.
 
* Many small bugs have been fixed.


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
