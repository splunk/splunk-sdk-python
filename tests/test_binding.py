#!/usr/bin/env python
#
# Copyright 2011 Splunk, Inc.
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

from os import path
from StringIO import StringIO
import sys
import unittest
import urllib2
import uuid
from xml.etree.ElementTree import XML

import splunk.binding as binding
from splunk.binding import HTTPError
import splunk.data as data

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

def read_module_baseline(filename):
    fd = open(filename, "r")
    baseline = fd.read().replace("\n", "")
    fd.close()
    return baseline

def check_module(modulename, filename):
    __import__(modulename)
    module = sys.modules[modulename]
    names = str(dir(module))
    baseline = read_module_baseline(filename)
    return names == baseline

class ModuleTestCase(unittest.TestCase):
    # Verify that the library modules contain what we expect (more or less)
    def test_names(self):
        modules = [
            "splunk",
            "splunk.binding",
            "splunk.client",
            "splunk.data",
            "splunk.results"
        ]
        for module in modules:
            self.assertTrue(check_module(module, module + ".baseline"))

def isatom(body):
    """Answers if the given response body looks like ATOM."""
    root = XML(body)
    return \
        root.tag == XNAME_FEED and \
        root.find(XNAME_AUTHOR) is not None and \
        root.find(XNAME_ID) is not None and \
        root.find(XNAME_TITLE) is not None

class ProtocolTestCase(unittest.TestCase):
    def test(self):
        global opts

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
    
class BindingTestCase(unittest.TestCase): # Base class
    def setUp(self):
        global opts
        self.context = binding.connect(**opts.kwargs)

    def tearDown(self):
        pass

    def connect(self, username, password, **kwargs):
        return binding.connect(
            scheme=self.context.scheme,
            host=self.context.host,
            port=self.context.port,
            username=username,
            password=password,
            **kwargs)

    def get(self, path, **kwargs):
        response = self.context.get(path, **kwargs)
        self.assertEqual(response.status, 200)
        return response

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

    def create(self, path, **kwargs):
        status = kwargs.get('status', 201)
        response = self.assertHttp(status, self.context.post, path, **kwargs)
        return response

    def delete(self, path, **kwargs):
        status = kwargs.get('status', 200) 
        response = self.assertHttp(status, self.context.delete, path, **kwargs)
        return response

    def update(self, path, **kwargs):
        status = kwargs.get('status', 200)
        response = self.assertHttp(status, self.context.post, path, **kwargs)
        return response

    def test(self):
        # Just check to make sure the service is alive
        self.assertEqual(self.get("/services").status, 200)

    def test_logout(self):
        response = self.context.get("/services")
        self.assertEqual(response.status, 200)

        self.context.logout()
        self.assertHttp(401, self.context.get, "/services")

        self.context.login()
        response = self.context.get("/services")
        self.assertEqual(response.status, 200)

# Use the binding layer to test some more extensive interactions with Splunk.
class UsersTestCase(BindingTestCase):
    def eqroles(self, username, roles):
        """Answer if the given user is in exactly the given roles."""
        user = self.user(username)
        roles = roles.split(',')
        if len(roles) != len(user.roles): return False
        for role in roles:
            if not role in user.roles: 
                return False
        return True
        
    def create_user(self, username, password, roles):
        self.assertFalse(username in self.users())
        self.create(PATH_USERS, name=username, password=password, roles=roles)
        self.assertTrue(username in self.users())

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
