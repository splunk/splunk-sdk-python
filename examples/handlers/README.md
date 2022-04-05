# Pluggable HTTP Request Handlers

The Splunk SDK library supports pluggable HTTP request handlers that enable
the library to be used with alternate HTTP request implementations.

This feature can be used to supply implementations with support for features
not included in the default request handler (which is based on httplib), such 
as support for HTTP proxies and server certificate validation. It can also be 
used to provide implementations with additional logging or diagnostic output 
for debugging.

This directory contains a collection of examples that demonstrate various 
alternative HTTP request handlers.

* **handler_urllib2.py** is a simple request handler implemented using urllib2.
  * Steps for creating certificate and privateKey - https://docs.splunk.com/Documentation/Splunk/8.2.4/Security/Howtoself-signcertificates
  * Update certfile, keyfile and password value for context.load_cert_chain() method

* **handler_debug.py** wraps the default request handler and prints some
  simple request information to stdout.

* **handler_proxy.py** implements support for HTTP requests via a proxy.

* **handler_certs.py** implements a hander that validates server certs.

