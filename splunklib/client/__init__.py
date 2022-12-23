# Copyright 2011-2015 Splunk, Inc.
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

"""The **splunklib.client** module provides a Pythonic interface to the
`Splunk REST API <http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI/RESTcontents>`_,
allowing you programmatically access Splunk's resources.

**splunklib.client** wraps a Pythonic layer around the wire-level
binding of the **splunklib.binding** module. The core of the library is the
:class:`Service` class, which encapsulates a connection to the server, and
provides access to the various aspects of Splunk's functionality, which are
exposed via the REST API. Typically you connect to a running Splunk instance
with the :func:`connect` function::

    import splunklib.client as client
    service = client.connect(host='localhost', port=8089,
                       username='admin', password='...')
    assert isinstance(service, client.Service)

:class:`Service` objects have fields for the various Splunk resources (such as apps,
jobs, saved searches, inputs, and indexes). All of these fields are
:class:`Collection` objects::

    appcollection = service.apps
    my_app = appcollection.create('my_app')
    my_app = appcollection['my_app']
    appcollection.delete('my_app')

The individual elements of the collection, in this case *applications*,
are subclasses of :class:`Entity`. An ``Entity`` object has fields for its
attributes, and methods that are specific to each kind of entity. For example::

    print(my_app['author'])  # Or: print(my_app.author)
    my_app.package()  # Creates a compressed package of this application
"""

from .BaseService import _BaseService
from .Endpoint import Endpoint
from .KVStoreCollectionData import KVStoreCollectionData
from .Service import Service


# kwargs: scheme, host, port, app, owner, username, password
def connect(**kwargs):
    """This function connects and logs in to a Splunk instance.

    This function is a shorthand for :meth:`Service.login`.
    The ``connect`` function makes one round trip to the server (for logging in).

    :param host: The host name (the default is "localhost").
    :type host: ``string``
    :param port: The port number (the default is 8089).
    :type port: ``integer``
    :param scheme: The scheme for accessing the service (the default is "https").
    :type scheme: "https" or "http"
    :param verify: Enable (True) or disable (False) SSL verification for
                   https connections. (optional, the default is True)
    :type verify: ``Boolean``
    :param `owner`: The owner context of the namespace (optional).
    :type owner: ``string``
    :param `app`: The app context of the namespace (optional).
    :type app: ``string``
    :param sharing: The sharing mode for the namespace (the default is "user").
    :type sharing: "global", "system", "app", or "user"
    :param `token`: The current session token (optional). Session tokens can be
                    shared across multiple service instances.
    :type token: ``string``
    :param cookie: A session cookie. When provided, you don't need to call :meth:`login`.
        This parameter is only supported for Splunk 6.2+.
    :type cookie: ``string``
    :param autologin: When ``True``, automatically tries to log in again if the
        session terminates.
    :type autologin: ``boolean``
    :param `username`: The Splunk account username, which is used to
                       authenticate the Splunk instance.
    :type username: ``string``
    :param `password`: The password for the Splunk account.
    :type password: ``string``
    :param retires: Number of retries for each HTTP connection (optional, the default is 0).
                    NOTE THAT THIS MAY INCREASE THE NUMBER OF ROUND TRIP CONNECTIONS TO THE SPLUNK SERVER.
    :type retries: ``int``
    :param retryDelay: How long to wait between connection attempts if `retries` > 0 (optional, defaults to 10s).
    :type retryDelay: ``int`` (in seconds)
    :param `context`: The SSLContext that can be used when setting verify=True (optional)
    :type context: ``SSLContext``
    :return: An initialized :class:`Service` connection.

    **Example**::

        import splunklib.client as client
        s = client.connect(...)
        a = s.apps["my_app"]
        ...
    """

    s = Service(**kwargs)
    s.login()
    return s
