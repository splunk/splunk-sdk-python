# Analytics Example

The Analytics example is meant as a sample implementation of a 
"mini-Google Analytics" or "mini-Mixpanel" style web service.

At its core, it allows for logging of arbitrary events together with arbitrary
`key=value` properties for each event. You don't need to define a schema
up front and some events can have more properties than others (even within
the same kind of event).

This type of service is especially suited to Splunk, given the temporal nature
of the data, together with the lack of schema and no need to update past events.

## Architecture

The main component of the Analytics example are two pieces of reusable code
meant to manage input and output of data into Splunk.

### AnalyticsTracker

The `input.py` file defines the "input" side of the Analytics service. If you 
wanted to log some analytics data in your app, you would have the `AnalyticsTracker`
class defined in this file in order to do so.

The `AnalyticsTracker` class encapsulates all the information required to log
events to Splunk. This includes the "application" name (think of it as a sort
of namespace, if you wanted to log multiple apps' worth of events into the
same Splunk instance) and Splunk connection parameters. It also takes
an optional "index" parameter, but that's there mostly for testing purposes.

So, for example, you could write an `AnalyticsTracker` like this:

```python
from analytics.input import AnalyticsTracker

splunk_opts = ...
tracker = AnalyticsTracker("myapp", splunk_opts)
```

Once you have an instance of the `AnalyticsTracker`, you can use it to track
your events. For example, if you wanted to log an event regarding a user 
logging in, and you wanted to add the name of the user and also his user 
agent, you could do something like this:

```python
userid = ...
username = ...
useragent = ...
tracker.track("login", distinct_id = user_id, "username"=username, "useragent"=useragent)
```

The first parameter is the name of the event you want to log. The `distinct_id`
parameter specifies a "unique ID". You can use the unique ID to group events,
for example if you only wanted to count unique logins by user_id. The rest of
the parameters are arbitrary `key=value` pairs that you can also extract.

Internally, when you ask the `AnalyticsTracker` to log an event, it will construct
a textual representation of that event. It will also make sure to encode all the 
content to fit properly in Splunk. For example, for the above event, it 
would look something like this:

```
2011-08-08T11:45:17.735045 application="myapp" event="login" distinct_id="..." analytics_prop__username="..." analytics_prop__useragent="..."
```

The reason that we use the `analytics_prop__` prefix is to make sure there is 
no ambiguity between known fields such as `application` and `event` and user
supplied `key=value=` properties.

### AnalyticsRetriever

Similarly to `AnalyticsTracker`, the `output.py` file defines the "output" side
of the Analytics service. If you want to extract the events you logged in using
`AnalyticsTracker`, you'd use the `AnalyticsRetriever` class.

Creating an `AnalyticsRetriever` instance is identical to the `AnalyticsTracker`:

```python
from analytics.output import AnalyticsRetriever

splunk_opts = ...
retriever = AnalyticsRetriever("myapp", splunk_opts)
```

Once you have an instance of the `AnalyticsRetriever`, you can use its variety
of methods in order to query information about events.

Executing each of the methods will execute a Splunk search, retrieve the
results, and transform them into a well-defined Python dictionary format.

#### Examples

Listing all applications:

```python
print retriever.applications()
```

Listing all the types of events in the system:

```python
print retriever.events()
```

Listing all the union of all the properties used for a particular event:

```python
event_name = "login"
print retriever.properties(event_name)
```

Getting all the values of a given property for some event:

```python
event_name = "login"
prop_name = "useragent"
print retriever.property_values(event_name, prop_name))
```

Getting a "graph" of event information over time for all events of a
specific application (this uses the default TimeRange.MONTH):

```python
print retriever.events_over_time()
```

Getting a graph of event information over time for a specific event:

```python
print retriever.events_over_time(event_name="login")
```

### server.py

The `server.py` file provides a sample "web app" built on top of the 
Analytics service. It lists applications, and for each application 
you can see a graph of events over time, properties, etc.

We make use of the excellent open source
[flot](http://code.google.com/p/flot/) graphing library to render
our Javascript graphs. We also use the [`bottle.py`](http://bottlepy.org)
micro-web framework.

## Running the Sample

In order to run the sample, you can simply execute:

	./server.py

And navigate to http://localhost:8080/applications. I suggest you input some
events in beforehand, though `server.py` logs some events itself
as you navigate the site (it's meta analytics!).

