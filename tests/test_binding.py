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
import sys
import unittest
import urllib2
import uuid
from xml.etree.ElementTree import XML

import splunklib.binding as binding
from splunklib.binding import HTTPError
import splunklib.data as data

from utils import parse

# splunkd endpoint paths
PATH_USERS = "authentication/users"

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

opts = None # Command line options

def entry_titles(text):
    """Returns list of atom entry titles from the given atom text."""
    entry = data.load(text).feed.entry
    if not isinstance(entry, list): entry = [entry]
    return [item.title for item in entry]

def isatom(body):
    """Answers if the given response body looks like ATOM."""
    root = XML(body)
    return \
        root.tag == XNAME_FEED and \
        root.find(XNAME_AUTHOR) is not None and \
        root.find(XNAME_ID) is not None and \
        root.find(XNAME_TITLE) is not None

def uname():
    """Creates a unique name."""
    return str(uuid.uuid1())

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

class BaseTestCase(unittest.TestCase):
    def assertHttp(self, allowed_error_codes, fn, *args, **kwargs):
        # This is a special case of "assertRaises", where we want to check
        # that HTTP calls return the right status.
        try:
            return fn(*args, **kwargs)
        except HTTPError as e:
            error_msg = "Unexpected error code: %d" % e.status
            if (isinstance(allowed_error_codes, list)):
                self.assertTrue(e.status in allowed_error_codes, error_msg)
            else:
                self.assertTrue(e.status == allowed_error_codes, error_msg)
        except Exception as e:
            self.fail("HTTPError not raised, caught %s instead", str(type(e)))
        return None

class TestCase(BaseTestCase):
    def setUp(self):
        self.context = binding.connect(**opts.kwargs)

    # Verify that we can connect to the service.
    def test_connect(self):
        # Just check to make sure the service is alive
        self.assertEqual(self.context.get("/services").status, 200)

        # Make sure we can open a socket to the service
        self.context.connect().close()

    # Verify that Context.fullpath behaves as expected.
    def test_fullpath(self):
        context = self.context

        # Verify that Context.fullpath works as expected.

        path = context.fullpath("foo", owner=None, app=None)
        self.assertEqual(path, "/services/foo")

        path = context.fullpath("foo", owner="me", app=None)
        self.assertEqual(path, "/servicesNS/me/-/foo")

        path = context.fullpath("foo", owner=None, app="MyApp")
        self.assertEqual(path, "/servicesNS/-/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp")
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp", sharing=None)
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp", sharing="user")
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp", sharing="app")
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp",sharing="global")
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        path = context.fullpath("foo", owner="me", app="MyApp",sharing="system")
        self.assertEqual(path, "/servicesNS/nobody/system/foo")

        # Verify constructing resource paths using context defaults

        kwargs = opts.kwargs.copy()
        if 'app' in kwargs: del kwargs['app']
        if 'owner' in kwargs: del kwargs['owner']

        context = binding.connect(**kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/services/foo")

        context = binding.connect(owner="me", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/me/-/foo")

        context = binding.connect(app="MyApp", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/-/MyApp/foo")

        context = binding.connect(owner="me", app="MyApp", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing=None, **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="user", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/me/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="app", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="global", **kwargs)
        path = context.fullpath("foo")
        self.assertEqual(path, "/servicesNS/nobody/MyApp/foo")

        context = binding.connect(
            owner="me", app="MyApp", sharing="system", **kwargs)
        path = context.fullpath("foo")
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
            context = binding.connect(handler=handler, **opts.kwargs)
            for path in paths:
                body = context.get(path).body.read()
                self.assertTrue(isatom(body))

    def test_logout(self):
        response = self.context.get("/services")
        self.assertEqual(response.status, 200)

        self.context.logout()
        self.assertHttp(401, self.context.get, "/services")

        self.context.login()
        response = self.context.get("/services")
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

            ({ 'sharing': "system", 'owner': "Bob", 'app': "search" },
             { 'sharing': "system", 'owner': "nobody", 'app': "system" })]

        for kwargs, expected in tests:
            namespace = binding.namespace(**kwargs)
            for k, v in expected.iteritems():
                self.assertEqual(namespace[k], v)

        with self.assertRaises(ValueError):
            binding.namespace(sharing="gobble")

# Use the binding layer to test some more extensive interactions with Splunk.
class UsersTestCase(BaseTestCase):
    def connect(self, username, password, **kwargs):
        return binding.connect(
            scheme=self.context.scheme,
            host=self.context.host,
            port=self.context.port,
            username=username,
            password=password,
            **kwargs)

    def create(self, path, **kwargs):
        status = kwargs.get('status', 201)
        response = self.assertHttp(status, self.context.post, path, **kwargs)
        return response

    def create_user(self, username, password, roles):
        self.assertFalse(username in self.users())
        self.create(PATH_USERS, name=username, password=password, roles=roles)
        self.assertTrue(username in self.users())

    def delete(self, path, **kwargs):
        status = kwargs.get('status', 200) 
        response = self.assertHttp(status, self.context.delete, path, **kwargs)
        return response

    def eqroles(self, username, roles):
        """Answer if the given user is in exactly the given roles."""
        user = self.user(username)
        roles = roles.split(',')
        if len(roles) != len(user.roles): return False
        for role in roles:
            if not role in user.roles: 
                return False
        return True

    def get(self, path, **kwargs):
        response = self.context.get(path, **kwargs)
        self.assertEqual(response.status, 200)
        return response

    def setUp(self):
        self.context = binding.connect(**opts.kwargs)

    def update(self, path, **kwargs):
        status = kwargs.get('status', 200)
        response = self.assertHttp(status, self.context.post, path, **kwargs)
        return response

    def user(self, username):
        """Returns entity value for given user name."""
        response = self.get("%s/%s" % (PATH_USERS, username))
        self.assertEqual(response.status, 200)
        body = response.body.read()
        self.assertEqual(XML(body).tag, XNAME_FEED)
        return data.load(body).feed.entry.content

    def users(self):
        """Returns a list of user names."""
        response = self.get(PATH_USERS)
        self.assertEqual(response.status, 200)
        body = response.body.read()
        self.assertEqual(XML(body).tag, XNAME_FEED)
        return entry_titles(body)

    def test(self):
        self.get(PATH_USERS)
        self.get(PATH_USERS + "/_new")

    def test_create(self):
        username = uname()
        password = "changeme"
        userpath = "%s/%s" % (PATH_USERS, username)

        # Can't create a user without a role
        self.create(PATH_USERS, name=username, password=password, status=400)

        # Create a test user
        self.create_user(username, password, "user")
        try:
            # Cannot create a duplicate
            self.create(
                PATH_USERS, 
                name=username, 
                password=password, 
                roles="user", 
                status=400) 

            # Connect as test user
            usercx = self.connect(username, password, owner=username)

            # Make sure the new context works
            response = usercx.get('/services')
            self.assertEquals(response.status, 200)

            # Test user does not have privs to create another user
            self.assertHttp(
                [403, 404], 
                usercx.post, 
                PATH_USERS, 
                name="flimzo", 
                password="dunno",
                roles="user")

            # User cannot delete themselves ..
            self.assertHttp([403, 404], usercx.delete, userpath)
    
        finally:
            self.delete(userpath)
            self.assertFalse(username in self.users())

    def test_edit(self):
        username = uname()
        password = "changeme"
        userpath = "%s/%s" % (PATH_USERS, username)

        self.create_user(username, password, "user")
        try:
            self.update(userpath, defaultApp="search")
            self.update(userpath, defaultApp=uname(), status=400)
            self.update(userpath, defaultApp="")
            self.update(userpath, realname="Renzo", email="email.me@now.com")
            self.update(userpath, realname="", email="")
        finally:
            self.delete(userpath)
            self.assertFalse(username in self.users())

    def test_password(self):
        username = uname()
        password = "changeme"
        userpath = "%s/%s" % (PATH_USERS, username)

        # Create a test user
        self.create_user(username, password, "user")
        try:
            # Connect as test user
            usercx = self.connect(username, password, owner=username)

            # User changes their own password
            response = usercx.post(userpath, password="changed")
            self.assertEqual(response.status, 200)

            # Change it again for giggles ..
            response = usercx.post(userpath, password="changeroo")
            self.assertEqual(response.status, 200)

            # Try to connect with original password ..
            self.assertRaises(HTTPError,
                self.connect, username, password, owner=username)

            # Admin changes it back
            self.update(userpath, password=password)

            # And now we can connect again with original password ..
            self.connect(username, password, owner=username)

        finally:
            self.delete(userpath)
            self.assertFalse(username in self.users())

    def test_roles(self):
        username = uname()
        password = "changeme"
        userpath = "%s/%s" % (PATH_USERS, username)

        # Create a test user
        self.create_user(username, password, "admin")
        try:
            self.assertTrue(self.eqroles(username, "admin"))

            # Update with multiple roles
            self.update(userpath, roles=["power", "user"])
            self.assertTrue(self.eqroles(username, "power,user"))

            # Set back to a single role
            self.update(userpath, roles="user")
            self.assertTrue(self.eqroles(username, "user"))

            # Fail adding unknown roles
            self.update(userpath, roles="__unknown__", status=400)

        finally:
            self.delete(userpath)
            self.assertTrue(username not in self.users())
        
if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    # Don't pass the Splunk cmdline args to unittest
    unittest.main(argv=sys.argv[:1])
