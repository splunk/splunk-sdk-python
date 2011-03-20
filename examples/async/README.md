# 'Async' use of the Python SDK

This example is meant to serve two purposes. The first is an example of how
to use the pluggable HTTP capabilities of the SDK binding layer, and the
other is how one could use a coroutine-based library to achieve high
concurrency with the SDK.

## Pluggable HTTP

The example provides an implementation of the Splunk HTTP class using
`urllib2` rather than the usual `httplib`. The reason is that most
coroutine-based concurrency libraries tend to provide a modified version
of `urllib2`. The implementation here is simplified: it does not handle
proxies, certificates and other advanced features. Instead, it just shows
how one could write a custom HTTP handling class for their usage of the SDK.

## Concurrency

You can run the example in two modes: synchronous and asynchronous.

### Synchronous Mode

To run the example in synchronous mode, use the following command:

	python async.py sync

This will execute the same search multiple times, and due to the 
synchronous nature of the builtin Python implementation of `urllib2`,
we will wait until each search is finished before moving on to the next
one.

### Asynchronous Mode

To run the example in asynchronous mode, use the following command:

	python async.py async

This will do the same thing as the synchronous version, except it will
use the [`eventlet`](http://eventlet.net/) library to do so. `eventlet`
provides its own version of the `urllib2` library, which makes full use
of its coroutine nature. This means that when we execute an HTTP request
(for example, `service.jobs.create(query, exec_mode="blocking")`), instead
of blocking the entire program until it returns, we will "switch" out of the
current context and into a new one. In the new context, we can issue another
HTTP request, which will in turn block, and we move to another context, and so
on. This allows us to have many requests "in-flight", and thus not block the 
execution of other requests.

In async mode, we finish the example in about a third of the time (relative to 
synchronous mdoe).