#!/usr/bin/env python
#
# Copyright 2011-2012 Splunk, Inc.
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

from StringIO import StringIO
import urllib2
import uuid
from xml.etree.ElementTree import XML

import testlib

import splunklib.binding as binding
from splunklib.binding import HTTPError, AuthenticationError, UrlEncoded
import splunklib.data as data

# splunkd endpoint paths
PATH_USERS = "authentication/users/"

# XML Namespaces
NAMESPACE_ATOM = "http://www.w3.org/2005/Atom"
NAMESPACE_REST = "http://dev.splunk.com/ns/rest"
NAMESPACE_OPENSEARCH = "http://a9.com/-/spec/opensearch/1.1"

# XML Extended Name Fragments
XNAMEF_ATOM = "{%s}%%s" % NAMESPACE_ATOM
XNAMEF_REST = "{%s}%%s" % NAMESPACE_REST
XNAMEF_OPENSEARCH = "{%s}%%s" % NAMESPACE_OPENSEARCH

# XML Extended Names
XNAME_AUTHOR = XNAMEF_ATOM % "author"
XNAME_ENTRY = XNAMEF_ATOM % "entry"
XNAME_FEED = XNAMEF_ATOM % "feed"
XNAME_ID = XNAMEF_ATOM % "id"
XNAME_TITLE = XNAMEF_ATOM % "title"

def isatom(body):
    """Answers if the given response body looks like ATOM."""
    root = XML(body)
    return \
        root.tag == XNAME_FEED and \
        root.find(XNAME_AUTHOR) is not None and \
        root.find(XNAME_ID) is not None and \
        root.find(XNAME_TITLE) is not None

def load(response):
    return data.load(response.body.read())

# An urllib2 based HTTP request handler, used to test the binding layers
# support for pluggable request handlers.
def urllib2_handler(url, message, **kwargs):
    method = message['method'].lower()
    data = message.get('body', "") if method == 'post' else None
    headers = dict(message.get('headers', []))
    context = urllib2.Request(url, data, headers)
    try:
        response = urllib2.urlopen(context)
    except urllib2.HTTPError, response:
        pass # Propagate HTTP errors via the returned response message
    return {
        'status': response.code,
        'reason': response.msg,
        'headers': response.info().dict,
        'body': StringIO(response.read())
    }

class TestCase(testlib.TestCase):
    def test_responsereader(self):
        txt = "This is a test of the emergency broadcasting system."
        response = binding.ResponseReader(StringIO(txt))
        self.assertEqual(response.read(), txt)

        response = binding.ResponseReader(StringIO(txt))
        self.assertEqual(response.peek(5), txt[:5])
        self.assertFalse(response.empty)
        self.assertEqual(response.read(), txt)
        self.assertTrue(response.empty)

        response = binding.ResponseReader(StringIO(""))
        self.assertTrue(response.empty)
        self.assertEqual(response.peek(1), "")
        self.assertTrue(response.empty)
        
        

    def test_urlencoded(self):
        self.assertTrue(isinstance(UrlEncoded('a') + UrlEncoded('b'), UrlEncoded))
        self.assertTrue(isinstance('a' + UrlEncoded('b'), UrlEncoded))
        self.assertTrue(isinstance(UrlEncoded('a') + 'b', UrlEncoded))
        def f():
            UrlEncoded('%s') % 'boris'
        self.assertRaises(TypeError, f)

    def test_authority(self):
        self.assertEqual(binding._authority(), 
                         "https://localhost:8089")
        self.assertEqual(binding._authority(host="splunk.utopia.net"),
                         "https://splunk.utopia.net:8089")
        self.assertEqual(binding._authority(host="2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
                         "https://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:8089")
        self.assertEqual(binding._authority(scheme="http", host="splunk.utopia.net", port="471"),
                         "http://splunk.utopia.net:471")

    # Verify that we can create (and delete) a resource
    def test_create(self):
        context = binding.connect(**self.opts.kwargs)

        username = "sdk-test-user"
        password = "changeme"
        roles = "power"

        try: 
            response = context.delete(PATH_USERS + username)
            self.assertEqual(response.status, 200)
        except HTTPError, e:
            self.assertEqual(e.status, 400) # User doesnt exist

        # Can't create a user without a role
        try:
            context.post(PATH_USERS, name=username, password=password)
            self.fail('Did not get an error creating a user without a role.')
        except HTTPError, e:
            self.assertEqual(e.status, 400)
        except: 
            self.fail('Got an unexpected error.')

        # Create a user with the required role
        response = context.post(
            PATH_USERS, name=username, password=password, roles=roles)
        self.assertEqual(response.status, 201)

        response = context.get(PATH_USERS + username)
        entry = load(response).feed.entry
        self.assertEqual(entry.title, username)

        context.delete(PATH_USERS + username)

    # Verify that we can connect to the service.
    def test_connect(self):
        context = binding.connect(**self.opts.kwargs)

        # Just check to make sure the service is alive
        response = context.get("/services")
        self.assertEqual(response.status, 200)

        # Make sure we can open a socket to the service
        context.connect().close()

    def test_autologin(self):
        opts = self.opts.kwargs
        opts['autologin'] = True
        context = binding.connect(**opts)

        self.assertEqual(context.get("/services").status, 200)
        context.logout()
        self.assertEqual(context.get("/services").status, 200)

        context.autologin = False
        context.logout()
        self.assertRaises(AuthenticationError, context.get, "/services")

    # Verify that Context._abspath behaves as expected.
    def test_abspath(self):
        context = binding.connect(**self.opts.kwargs)

        # Verify that Context._abspath works as expected.

        path = context._abspath("foo", owner=None, app=None)
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/services/foo")

        path = context._abspath("foo", owner="me", app=None)
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/-/foo")

        path = context._abspath("foo", owner=None, app="MyApp")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/-/MyApp/foo")

        path = context._abspath("foo", owner="me", app="MyApp")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context._abspath("foo", owner="me", app="MyApp", sharing=None)
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context._abspath("foo", owner="me", app="MyApp", sharing="user")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context._abspath("foo", owner="me", app="MyApp", sharing="app")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        path = context._abspath("foo", owner="me", app="MyApp",sharing="global")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        path = context._abspath("foo bar", owner="me", app="MyApp",sharing="system")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/system/foo%20bar")

        path = context._abspath('/a/b c/d')
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, '/a/b%20c/d')

        # Verify constructing resource paths using context defaults

        kwargs = self.opts.kwargs.copy()
        if 'app' in kwargs: del kwargs['app']
        if 'owner' in kwargs: del kwargs['owner']

        context = binding.connect(**kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/services/foo")

        context = binding.connect(owner="me", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/-/foo")

        context = binding.connect(app="MyApp", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/-/MyApp/foo")

        context = binding.connect(owner="me", app="MyApp", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing=None, **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="user", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="app", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="global", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="system", **kwargs)
        path = context._abspath("foo")
        self.assertTrue(isinstance(path, UrlEncoded))
        self.assertEqual(path, "/servicesNS/nobody/system/foo")

    # Verify pluggable HTTP reqeust handlers.
    def test_handlers(self):
        paths = [
            "/services", 
            "authentication/users", 
            "search/jobs"
        ]

        handlers = [
            binding.handler(),  # default handler
            urllib2_handler,
        ]

        for handler in handlers:
            context = binding.connect(handler=handler, **self.opts.kwargs)
            for path in paths:
                body = context.get(path).body.read()
                self.assertTrue(isatom(body))

    def test_list(self):
        context = binding.connect(**self.opts.kwargs)

        response = context.get(PATH_USERS)
        self.assertEqual(response.status, 200)

        response = context.get(PATH_USERS + "/_new")
        self.assertEqual(response.status, 200)

    def test_logout(self):
        context = binding.connect(**self.opts.kwargs)

        response = context.get("/services")
        self.assertEqual(response.status, 200)

        context.logout()
        try:
            context.get("/services")
            self.fail('Did not get an error from GETing from a logged out Context.')
        except AuthenticationError, e:
            pass
        except: self.fail('Got an unexpected error from GETing from a logged out Context.')

        try:
            context.post('/services')
            self.fail('Did not get an error from POSTing to a logged out Context')
        except AuthenticationError, e:
            pass
        except:
            self.fail('Got an unexpected error from POSTing to a logged out Context.')

        try:
            context.delete('/services')
            self.fail('Did not get an error from POSTing to a logged out Context')
        except AuthenticationError, e:
            pass
        except:
            self.fail('Got an unexpected error from POSTing to a logged out Context.')

        context.login()
        response = context.get("/services")
        self.assertEqual(response.status, 200)

    def test_namespace(self):
        tests = [
            ({ },
             { 'sharing': None, 'owner': None, 'app': None }),

            ({ 'owner': "Bob" },
             { 'sharing': None, 'owner': "Bob", 'app': None }),

            ({ 'app': "search" },
             { 'sharing': None, 'owner': None, 'app': "search" }),

            ({ 'owner': "Bob", 'app': "search" },
             { 'sharing': None, 'owner': "Bob", 'app': "search" }),

            ({ 'sharing': "user" },
             { 'sharing': "user", 'owner': None, 'app': None }),

            ({ 'sharing': "user", 'owner': "Bob" },
             { 'sharing': "user", 'owner': "Bob", 'app': None }),

            ({ 'sharing': "user", 'app': "search" },
             { 'sharing': "user", 'owner': None, 'app': "search" }),

            ({ 'sharing': "user", 'owner': "Bob", 'app': "search" },
             { 'sharing': "user", 'owner': "Bob", 'app': "search" }),

            ({ 'sharing': "app" },
             { 'sharing': "app", 'owner': "nobody", 'app': None }),

            ({ 'sharing': "app", 'owner': "Bob" },
             { 'sharing': "app", 'owner': "nobody", 'app': None }),

            ({ 'sharing': "app", 'app': "search" },
             { 'sharing': "app", 'owner': "nobody", 'app': "search" }),

            ({ 'sharing': "app", 'owner': "Bob", 'app': "search" },
             { 'sharing': "app", 'owner': "nobody", 'app': "search" }),

            ({ 'sharing': "global" },
             { 'sharing': "global", 'owner': "nobody", 'app': None }),

            ({ 'sharing': "global", 'owner': "Bob" },
             { 'sharing': "global", 'owner': "nobody", 'app': None }),

            ({ 'sharing': "global", 'app': "search" },
             { 'sharing': "global", 'owner': "nobody", 'app': "search" }),

            ({ 'sharing': "global", 'owner': "Bob", 'app': "search" },
             { 'sharing': "global", 'owner': "nobody", 'app': "search" }),

            ({ 'sharing': "system" },
             { 'sharing': "system", 'owner': "nobody", 'app': "system" }),

            ({ 'sharing': "system", 'owner': "Bob" },
             { 'sharing': "system", 'owner': "nobody", 'app': "system" }),

            ({ 'sharing': "system", 'app': "search" },
             { 'sharing': "system", 'owner': "nobody", 'app': "system" }),

            ({ 'sharing': "system", 'owner': "Bob",    'app': "search" },
             { 'sharing': "system", 'owner': "nobody", 'app': "system" }),

            ({ 'sharing': 'user',   'owner': '-',      'app': '-'},
             { 'sharing': 'user',   'owner': '-',      'app': '-'})]

        for kwargs, expected in tests:
            namespace = binding.namespace(**kwargs)
            for k, v in expected.iteritems():
                self.assertEqual(namespace[k], v)

        with self.assertRaises(ValueError):
            binding.namespace(sharing="gobble")

    # Verify that we can update a resource
    def test_update(self):
        context = binding.connect(**self.opts.kwargs)

        username = "sdk-test-user"
        password = "changeme"
        roles = ["power", "user"]

        try: 
            response = context.delete(PATH_USERS + username)
            self.assertEqual(response.status, 200)
        except HTTPError, e:
            self.assertEqual(e.status, 400) # User doesnt exist

        # Create the test user
        response = context.post(
            PATH_USERS, name=username, password=password, roles=roles)
        self.assertEqual(response.status, 201)

        response = context.get(PATH_USERS + username)
        self.assertEqual(response.status, 200)
        entry = load(response).feed.entry
        self.assertEqual(entry.title, username)

        # Update the test user
        response = context.post(
            PATH_USERS + username,
            defaultApp="search",
            realname="Renzo",
            email="email.me@now.com")
        self.assertEqual(response.status, 200)

        response = context.get(PATH_USERS + username)
        self.assertEqual(response.status, 200)
        entry = load(response).feed.entry
        self.assertEqual(entry.title, username)
        self.assertEqual(entry.content.defaultApp, "search")
        self.assertEqual(entry.content.realname, "Renzo")
        self.assertEqual(entry.content.email, "email.me@now.com")

        context.delete(PATH_USERS + username)
        
    # Verify that we can pass a pre-existing token
    def test_preexisting_token(self):
        context = binding.connect(**self.opts.kwargs)
        token = context.token
        
        # Ensure the context works
        response = context.get("/services")
        self.assertEqual(response.status, 200)
        
        # Create a new opts dictionary and stash the token there
        opts = self.opts.kwargs.copy()
        opts["token"] = token
        
        # We create a new context
        newContext = binding.Context(**opts)
        
        # Ensure the new context works
        response = newContext.get("/services")
        self.assertEqual(response.status, 200)
        
        # Make sure we can open a socket to the service
        context.connect().close()
        newContext.connect().close()
        
if __name__ == "__main__":
    testlib.main()
