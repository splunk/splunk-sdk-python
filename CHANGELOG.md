# Splunk Python SDK Changelog

## develop

### Features

* Added support for IPv6, can now connect to a splunkd listening on an IPv6 
  address.
* Improvements to unit tests

### Breaking changes

* Renamed the core module from `splunk` to `splunklib`. The Splunk product 
  already ships with an internal Python module named `splunk` and the name 
  conflict with the SDK prevented installing the SDK into Splunk Python sandbox
  for use by Splunk extensions.

* Update all classes in the core library modules to use new-style classes
* Rename Job.setpriority to Job.set_priority
* Rename Job.setttl to Job.set_ttl

* Naming context - previously the binding context (`binding.Context`) and all
  tests & samples took a single (optional) `namespace` argument that specified
  both the app and owner names to use for the binding context. However, the
  underlying Splunk REST API takes these as separate `app` and `owner` arguments
  and it turned out to be more convenient to reflect these arguments directly
  in the SDK, so the binding context (and all samples & test) now take separate
  (and optional) `app` and `owner` arguments instead of the prior `namespace` 
  argument.

  You can find a detailed description of Splunk namespaces in the Splunk REST
  API reference under the section on accessing Splunk resources at:

  * http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTresources

### Bug fixes

* Fix for GitHub Issues: 10, 12, 17, 21
* Fix for incorrect handling of mixed case new user names (need to account for
  fact that Splunk automatically lowercases)
* Fix for Service.settings so that updates get sent to the correct endpoint
* Check name arg passed to Collection.create and raise ValueError if not
  a basestring
* Fix handling of resource names that are not valid URL segments by quoting the
  resource name when constructing its path

## v0.1.0a

* Fix a bug in the dashboard example
* Ramp up README with more info

## v0.1.0

* Initial Python SDK release
