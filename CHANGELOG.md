# Splunk Enterprise SDK for Python Changelog

## Version 2.0.0-beta

### Feature updates
* `ensure_binary`, `ensure_str`, `ensure_text` and `assert_regex` utility methods have been migrated from `six.py` to `splunklib/__init__.py`

### Major changes
* Removed Code specific to Python2
* Removed six.py dependency
* Removed `__future__` imports
* Refactored & Updated `splunklib` and `tests` to utilise Python3 features
* Updated CI test matrix to run with Python versions - 3.7 and 3.9
* Refactored Code throwing `deprecation` warnings
* Refactored Code violating Pylint rules
## Version 1.7.4

### Bug fixes
* [#532](https://github.com/splunk/splunk-sdk-python/pull/532) update encoding errors mode to 'replace' [[issue#505](https://github.com/splunk/splunk-sdk-python/issues/505)]
* [#507](https://github.com/splunk/splunk-sdk-python/pull/507) masked sensitive data in logs [[issue#506](https://github.com/splunk/splunk-sdk-python/issues/506)]

### Minor changes
* [#530](https://github.com/splunk/splunk-sdk-python/pull/530) Update GitHub CI build status in README and removed RTD(Read The Docs) reference

## Version 1.7.3

### Bug fixes
* [#493](https://github.com/splunk/splunk-sdk-python/pull/493) Fixed file permission for event_writer.py file [[issue#487](https://github.com/splunk/splunk-sdk-python/issues/487)]
* [#500](https://github.com/splunk/splunk-sdk-python/pull/500) Replaced index_field with accelerated_field for kvstore [[issue#497](https://github.com/splunk/splunk-sdk-python/issues/497)]
* [#502](https://github.com/splunk/splunk-sdk-python/pull/502) Updated check for IPv6 addresses

### Minor changes
* [#490](https://github.com/splunk/splunk-sdk-python/pull/490) Added ACL properties update feature
* [#495](https://github.com/splunk/splunk-sdk-python/pull/495) Added Splunk 8.1 in GitHub Actions Matrix
* [#485](https://github.com/splunk/splunk-sdk-python/pull/485) Added test case for cookie persistence
* [#503](https://github.com/splunk/splunk-sdk-python/pull/503) README updates on accessing "service" instance in CSC and ModularInput apps
* [#504](https://github.com/splunk/splunk-sdk-python/pull/504) Updated authentication token names in docs to reduce confusion
* [#494](https://github.com/splunk/splunk-sdk-python/pull/494) Reuse splunklib.__version__ in handler.request 

## Version 1.7.2

### Minor changes
* [#482](https://github.com/splunk/splunk-sdk-python/pull/482) Special handling related to the semantic versioning of specific Search APIs functional in Splunk Enterprise 9.0.2 and (Splunk Cloud 9.0.2209). These SDK changes will enable seamless transition between the APIs based on the version of the Splunk Enterprise in use

## Version 1.7.1

### Bug fixes
* [#471](https://github.com/splunk/splunk-sdk-python/pull/471) Fixed support of Load Balancer "sticky sessions" (persistent cookies) [[issue#438](https://github.com/splunk/splunk-sdk-python/issues/438)]

### Minor changes
* [#466](https://github.com/splunk/splunk-sdk-python/pull/466) tests for CSC apps
* [#467](https://github.com/splunk/splunk-sdk-python/pull/467) Added 'kwargs' parameter for Saved Search History function
* [#475](https://github.com/splunk/splunk-sdk-python/pull/475) README updates

## Version 1.7.0

### New features and APIs
* [#468](https://github.com/splunk/splunk-sdk-python/pull/468) SDK Support for splunkd search API changes

### Bug fixes
* [#464](https://github.com/splunk/splunk-sdk-python/pull/464) updated checks for wildcards in StoragePasswords [[issue#458](https://github.com/splunk/splunk-sdk-python/issues/458)]

### Minor changes
* [#463](https://github.com/splunk/splunk-sdk-python/pull/463) Preserve thirdparty cookies

## Version 1.6.20

### New features and APIs
* [#442](https://github.com/splunk/splunk-sdk-python/pull/442) Optional retries feature added
* [#447](https://github.com/splunk/splunk-sdk-python/pull/447) Create job support for "output_mode:json" [[issue#285](https://github.com/splunk/splunk-sdk-python/issues/285)]

### Bug fixes
* [#449](https://github.com/splunk/splunk-sdk-python/pull/449) Set cookie [[issue#438](https://github.com/splunk/splunk-sdk-python/issues/438)]
* [#460](https://github.com/splunk/splunk-sdk-python/pull/460) Remove restart from client.Entity.disable

### Minor changes
* [#444](https://github.com/splunk/splunk-sdk-python/pull/444) Update tox.ini
* [#446](https://github.com/splunk/splunk-sdk-python/pull/446) Release workflow refactor
* [#448](https://github.com/splunk/splunk-sdk-python/pull/448) Documentation changes
* [#450](https://github.com/splunk/splunk-sdk-python/pull/450) Removed examples and it's references from the SDK


## Version 1.6.19

### New features and APIs
* [#441](https://github.com/splunk/splunk-sdk-python/pull/441) JSONResultsReader added and deprecated ResultsReader
  * Pre-requisite: Query parameter 'output_mode' must be set to 'json'
  * Improves performance by approx ~80-90%
  * ResultsReader is deprecated and will be removed in future releases (NOTE: Please migrate to JSONResultsReader)
* [#437](https://github.com/splunk/splunk-sdk-python/pull/437) added setup_logging() method in splunklib for logging
* [#426](https://github.com/splunk/splunk-sdk-python/pull/426) Added new github_commit modular input example
* [#392](https://github.com/splunk/splunk-sdk-python/pull/392) Break out search argument to option parsing for v2 custom search commands
* [#384](https://github.com/splunk/splunk-sdk-python/pull/384) Added Float parameter validator for custom search commands
* [#371](https://github.com/splunk/splunk-sdk-python/pull/371) Modinput preserve 'app' context

### Bug fixes
* [#439](https://github.com/splunk/splunk-sdk-python/pull/439) Modified POST method debug log to not log sensitive body/data
* [#431](https://github.com/splunk/splunk-sdk-python/pull/431) Add distsearch.conf to Stream Search Command examples [ [issue#418](https://github.com/splunk/splunk-sdk-python/issues/418) ]
* [#419](https://github.com/splunk/splunk-sdk-python/pull/419) Hec endpoint issue[ [issue#345](https://github.com/splunk/splunk-sdk-python/issues/345) ]
* [#416](https://github.com/splunk/splunk-sdk-python/pull/416) Removed strip() method in load_value() method from data.py file [ [issue#400](https://github.com/splunk/splunk-sdk-python/issues/400) ]
* [#148](https://github.com/splunk/splunk-sdk-python/pull/148) Identical entity names will cause an infinite loop

### Minor changes
* [#440](https://github.com/splunk/splunk-sdk-python/pull/440) Github release workflow modified to generate docs
* [#430](https://github.com/splunk/splunk-sdk-python/pull/430) Fix indentation in README
* [#429](https://github.com/splunk/splunk-sdk-python/pull/429) documented how to access modular input metadata
* [#427](https://github.com/splunk/splunk-sdk-python/pull/427) Replace .splunkrc with .env file in test and examples
* [#424](https://github.com/splunk/splunk-sdk-python/pull/424) Float validator test fix
* [#423](https://github.com/splunk/splunk-sdk-python/pull/423) Python3 compatibility for ResponseReader.__str__()
* [#422](https://github.com/splunk/splunk-sdk-python/pull/422) ordereddict and all its reference removed
* [#421](https://github.com/splunk/splunk-sdk-python/pull/421) Update README.md
* [#387](https://github.com/splunk/splunk-sdk-python/pull/387) Update filter.py
* [#331](https://github.com/splunk/splunk-sdk-python/pull/331) Fix a couple of warnings spotted when running python 2.7 tests
* [#330](https://github.com/splunk/splunk-sdk-python/pull/330) client: use six.string_types instead of basestring
* [#329](https://github.com/splunk/splunk-sdk-python/pull/329) client: remove outdated comment in Index.submit
* [#262](https://github.com/splunk/splunk-sdk-python/pull/262) properly add parameters to request based on the method of the request
* [#237](https://github.com/splunk/splunk-sdk-python/pull/237) Don't output close tags if you haven't written a start tag
* [#149](https://github.com/splunk/splunk-sdk-python/pull/149) "handlers" stanza missing in examples/searchcommands_template/default/logging.conf

## Version 1.6.18

### Bug fixes
* [#405](https://github.com/splunk/splunk-sdk-python/pull/405) Fix searchcommands_app example
* [#406](https://github.com/splunk/splunk-sdk-python/pull/406) Fix mod inputs examples
* [#407](https://github.com/splunk/splunk-sdk-python/pull/407) Fixed issue with Streaming and Generating Custom Search Commands dropping fields that aren't present in the first row of results. More details on how to opt-in to this fix can be found here: 
https://github.com/splunk/splunk-sdk-python/blob/develop/README.md#customization [ [issue#401](https://github.com/splunk/splunk-sdk-python/issues/401) ]

### Minor changes
* [#408](https://github.com/splunk/splunk-sdk-python/pull/408) Add search mode example
* [#409](https://github.com/splunk/splunk-sdk-python/pull/409) Add Support for authorization tokens read from .splunkrc [ [issue#388](https://github.com/splunk/splunk-sdk-python/issues/388) ]
* [#413](https://github.com/splunk/splunk-sdk-python/pull/413) Default kvstore owner to nobody [ [issue#231](https://github.com/splunk/splunk-sdk-python/issues/231) ]

## Version 1.6.17

### Bug fixes

* [#383](https://github.com/splunk/splunk-sdk-python/pull/383) Implemented the possibility to provide a SSLContext object to the connect method
* [#396](https://github.com/splunk/splunk-sdk-python/pull/396) Updated KVStore Methods to support dictionaries
* [#397](https://github.com/splunk/splunk-sdk-python/pull/397) Added code changes for encoding '/' in _key parameter in kvstore.data APIs.
* [#398](https://github.com/splunk/splunk-sdk-python/pull/398) Added dictionary support for KVStore "query" methods.
* [#402](https://github.com/splunk/splunk-sdk-python/pull/402) Fixed regression introduced in 1.6.15 to once again allow processing of empty input records in custom search commands (fix [#376](https://github.com/splunk/splunk-sdk-python/issues/376))
* [#404](https://github.com/splunk/splunk-sdk-python/pull/404) Fixed test case failure for 8.0 and latest(8.2.x) splunk version

### Minor changes

* [#381](https://github.com/splunk/splunk-sdk-python/pull/381) Updated current year in conf.py
* [#389](https://github.com/splunk/splunk-sdk-python/pull/389) Fixed few typos
* [#391](https://github.com/splunk/splunk-sdk-python/pull/391) Fixed spelling error in client.py
* [#393](https://github.com/splunk/splunk-sdk-python/pull/393) Updated development status past 3
* [#394](https://github.com/splunk/splunk-sdk-python/pull/394) Updated Readme steps to run examples
* [#395](https://github.com/splunk/splunk-sdk-python/pull/395) Updated random_number.py
* [#399](https://github.com/splunk/splunk-sdk-python/pull/399) Moved CI tests to GitHub Actions
* [#403](https://github.com/splunk/splunk-sdk-python/pull/403) Removed usage of Easy_install to install SDK

## Version 1.6.16

### Bug fixes
[#312](https://github.com/splunk/splunk-sdk-python/pull/312) Fix issue [#309](https://github.com/splunk/splunk-sdk-python/issues/309), avoid catastrophic backtracking in searchcommands

## Version 1.6.15

### Bug fixes

* [#301](https://github.com/splunk/splunk-sdk-python/pull/301) Fix chunk synchronization
* [#327](https://github.com/splunk/splunk-sdk-python/pull/327) Rename and cleanup follow-up for chunk synchronization
* [#352](https://github.com/splunk/splunk-sdk-python/pull/352) Allow supplying of a key-value body when calling Context.post()

### Minor changes

* [#350](https://github.com/splunk/splunk-sdk-python/pull/350) Initial end-to-end tests for streaming, reporting, generating custom search commands
* [#348](https://github.com/splunk/splunk-sdk-python/pull/348) Update copyright years to 2020 
* [#346](https://github.com/splunk/splunk-sdk-python/pull/346) Readme updates to urls, terminology, and formatting
* [#317](https://github.com/splunk/splunk-sdk-python/pull/317) Fix deprecation warnings

## Version 1.6.14

### Bug fix
* `SearchCommand` now correctly supports multibyte characters in Python 3.

## Version 1.6.13

### Bug fix
* Fixed regression in mod inputs which resulted in error ’file' object has no attribute 'readable’, by not forcing to text/bytes in mod inputs event writer any longer.

### Minor changes
* Minor updates to the splunklib search commands to support Python3

## Version 1.6.12

### New features and APIs
* Added Bearer token support using Splunk Token in v7.3
* Made modinput text consistent

### Bug fixes
* Changed permissions from 755 to 644 for python files to pass appinspect checks
* Removed version check on ssl verify toggle

## Version 1.6.11

### Bug Fix

* Fix custom search command V2 failures on Windows for Python3

## Version 1.6.10

### Bug Fix

* Fix long type gets wrong values on windows for python 2

## Version 1.6.9

### Bug Fix

* Fix buffered input in python 3

## Version 1.6.8

### Bug Fix

* Fix custom search command on python 3 on windows

## Version 1.6.7

### Changes

* Updated the Splunk Enterprise SDK for Python to work with the Python 3 version of Splunk Enterprise on Windows
* Improved the performance of deleting/updating an input
* Added logging to custom search commands app to showcase how to do logging in custom search commands by using the Splunk Enterprise SDK for Python

## Version 1.6.6

### Bug fixes

* Fix ssl verify to require certs when true

### Minor changes

* Make the explorer example compatible w/ Python 3
* Add full support for unicode in SearchCommands
* Add return code for invalid_args block

## Version 1.6.5

### Bug fixes

* Fixed XML responses to not throw errors for unicode characters.

## Version 1.6.4

### New features and APIs

Not Applicable

### Minor Changes

* Changed `splunklib/binding.py` Context class' constructor initialization to support default settings for encrypted http communication when creating the HttpLib object that it depends on. This is extracted from the keyword dictionary that is provided for its initializaiton. Encryption defaults to enabled if not specified.
* Changed `splunklib/binding.py` HttpLib class constructor to include the `verify` parameter in order to support default encryption if the default handler is being used. Encryption defaults to enabled if not specified.
* Changed `splunklib/binding.py` `handler` function to include the `verify` parameter in order to support default encryption.
* Changed `splunklib/binding.py` `handler`'s nested `connect` function to create the context in as unverified if specified by the `verify` parameter.

### Bug fixes

Not Applicable

### Documentation

* Changed `examples/searchcommands_app/package/bin/filter.py` FilterCommand.update doc-string from `map` to `update` in order to align with Splunk search changes.
* Changed `examples/searchcommands_app/package/default/searchbnf.conf` [filter-command].example1 from the `map` keyword to the `update` keyword in order to align with Splunk search changes.
* Changed `splunklib/binding.py` Context class' doc-string to include the `verify` parameter and type information related to the new keyword dictionary parameter `verify`.
* Changed `splunklib/binding.py` `handler` function's doc-string to include the `verify` parameter and type information related to the parameter `verify`.
* Changed `splunklib/client.py` `connect` function doc-string to include the `verify` parameter and type information related to the new keyword dictionary parameter `verify`.
* Changed `splunklib/client.py` `Service` Class' doc-string to include the `verify` parameter and type information related to the new keyword dictionary parameter `verify`.

## Version 1.6.3

### New features and APIs

* Support for Python 3.x has been added for external integrations with the Splunk platform. However, because Splunk Enterprise 7+ still includes Python 2.7.x, any apps or scripts that run on the Splunk platform must continue to be written for Python 2.7.x.

### Bug fixes

The following bugs have been fixed:

* Search commands error - `ERROR ChunkedExternProcessor - Invalid custom search command type: eventing`.

* Search commands running more than once for certain cases.

* Search command protocol v2 inverting the `distributed` configuration flag.

## Version 1.6.2

### Minor changes

* Use relative imports throughout the the SDK.

* Performance improvement when constructing `Input` entity paths.

## Version 1.6.1

### Bug Fixes

* Fixed Search Commands exiting if the external process returns a zero status code (Windows only).

* Fixed Search Command Protocol v2 not parsing the `maxresultrows` and `command` metadata properties.

* Fixed double prepending the `Splunk ` prefix for authentication tokens.

* Fixed `Index.submit()` for namespaced `Service` instances.

* Fixed uncaught `AttributeError` when accessing `Entity` properties (GitHub issue #131).

### Minor Changes

* Fixed broken tests due to expired SSL certificate.

## Version 1.6.0

### New Features and APIs

* Added support for KV Store.

* Added support for HTTP basic authentication (GitHub issue #117).

* Improve support for HTTP keep-alive connections (GitHub issue #122).


### Bug Fixes

* Fixed Python 2.6 compatibility (GitHub issue #141).

* Fixed appending restrictToHost to UDP inputs (GitHub issue #128).

### Minor Changes

* Added support for Travis CI.

* Updated the default test runner.

* Removed shortened links from documentation and comments.

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

* Fix `SearchCommands` decorators and `Validator` classes (GitHub issue #113).

* Fix `SearchCommands` bug iterating over `None` in `dict_reader.fieldnames` (GitHub issue #110).

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

