# The ABCs of Calling the Splunk REST API

This example shows three different approaches to making calls against the
Splunk REST API.

The examples all happen to retrieve a list of installed apps from a given 
Splunk instance, but they could apply as easily to any other area of the REST
API.

* **a.py** uses Python's standard httplib module to make calls against the 
  Splunk REST API. This example does not use any SDK libraries to access 
  Splunk. 

* **b.py** users the SDK's lower level binding module to access the REST API. 
  The binding module handles authentication details (and some additional book-
  keeping details not demonstrated by this sample) and the result is a much
  simplified interaction with Splunk, but its still very much a 'wire' level
  coding experience.

* **c.py** uses the SDK client module, which abstracts away most most of the 
  wire level details of invoking the REST API, but that still presents a 
  stateless interface to Splunk the attempts to faithfully represent the 
  semantics of the underlying REST API.

