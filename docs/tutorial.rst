Introduction
------------

Here's a simple program using the Python SDK. Obviously you'll have to
change the host, username, password, and any other data that you may
have customized. And don't experiment on your production Splunk
server! Install the free version of Splunk on your own machine to
experiment.::

    import splunklib.client as client
    c = client.connect(host="localhost",
                        port=8089,
                        scheme="https",
                        username="admin",
                        password="changeme")
    saved_searches = c.saved_searches
    mss = saved_searches.create("my_saved_search", "search * | head 10")
    assert "my_saved_search" in saved_searches
    saved_searches.delete("my_saved_search")

It's worth spending a few minute in ``ipython`` examining the objects
produced in this example. ``c`` is a ``Service``[[TODO: link to
reference docs]], which has [fields](link to list of fields in
Service's docs) that provide access to most of Splunk's contents.
``saved_searches`` is a ``Collection``, and each entity in it is
identified by a unique name (``"my_saved_search"`` in the example).
All the names should be alphanumeric plus ``_`` and ``-``; no spaces
are allowed[#]_.

.. [#] Splunk has two names for each entity: the pretty one meant to
be displayed to users in the web browser, and the alphanumeric one
that shows up in the URL of the REST call. It is the latter that is
used in the SDK. Thus the Search app in Splunk is called "Search"
in the web interface, but to fetch it via the SDK, you would write
``c.apps['search']``, not ``c.apps['Search']``. The "Getting
Started" app is ``c.apps['gettingstarted']``, not ``c.apps['Getting Started']``.

A ``Collection`` acts like a dictionary. You can call ``keys``,
``iteritems``, and ``itervalues`` just like on a dictionary. However,
you cannot assign to keys. ``saved_searches['some_name'] = ...`` is
nonsense. Use the ``create`` method instead. Also, 
``del saved_searches['some_name']`` does not currently work. Use the
``delete`` method instead.

Note that in the example code we did not assert::

    mss == saved_searches["my_saved_search"]

The Python objects you are manipulating represent snapshots of the
server's state at some point in the past. There is no good way of
defining equality on these that isn't misleading in many cases, so we
have made ``==`` and ``!=`` raise exceptions for entities.

Another side effect of using snapshots: after we delete the saved
search in the example, ``mss`` is still bound to the same local object
representing that search, even though it no longer exists on the
server. If you need to update your snapshot, call the ``refresh``
method[#]_. For more on caching and snapshots, see [[TODO: link to
section on roundtrips and caching]]

.. [#] Calling ``refresh`` on an entity that has already been deleted
raises an ``HTTPError``.

You can access the fields of an entity either as if they were keys in
a dictionary, or fields of an object::

    mss['search'] == "search * | head 10"
    mss.search    == "search * | head 10"

    mss['action.email'] == '0'
    mss.action.email    == '0'

A ``.`` isn't a valid character in identifiers in Python. The second
form is actually a series of field lookups. As as side effect, you can
get groups of fields that share prefixes.::

    mss['action'] == {'email': '0',
                      'populate_lookup': '0',
                      'rss': '0',
                      'script': '0',
                      'summary_index': '0'}
    mss.action == {'email': '0',
                   'populate_lookup': '0',
                   'rss': '0',
                   'script': '0',
                   'summary_index': '0'}

Those look like dictionaries, but they're actually a subclass called
``Record`` [[TODO: link to reference documentation]] that allows keys
to be looked up as fields. [[TODO: Implement keys() on entities, and
document it here]] In addition to fields, each kind of entity has a
range of methods.::

    mss.dispatch()    # Runs the saved search.
    mss.suppress(30)  # Suppress all alerts from this saved search for 30 seconds

This should be enough information to understand the reference
documentation and start using the SDK productively.

Roundtrips and caching
----------------------

The rate limiting step in most programs that call REST APIs is calls
to the server. The SDK is designed to minimize and postpone these as
much as possible. When you fetch an object from the SDK, you get a
snapshot. If there are updates on the server after that snapshot, you
won't know about them until you call ``refresh`` on your object. The
object might even have been deleted.





