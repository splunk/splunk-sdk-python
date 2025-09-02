#!/usr/bin/env python
#
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

from __future__ import absolute_import
from splunklib.binding import HTTPError
from tests import testlib
import logging

import splunklib.client as client
from splunklib import results

import pytest


@pytest.mark.smoke
class TestMacro(testlib.SDKTestCase):
    def setUp(self):
        super(TestMacro, self).setUp()
        macros = self.service.macros
        logging.debug("Macros namespace: %s", macros.service.namespace)
        self.macro_name = testlib.tmpname()
        definition = '| eval test="123"'
        self.macro = macros.create(self.macro_name, definition)

    def tearDown(self):
        super(TestMacro, self).setUp()
        for macro in self.service.macros:
            if macro.name.startswith("delete-me"):
                self.service.macros.delete(macro.name)

    def check_macro(self, macro):
        self.check_entity(macro)
        expected_fields = ["definition", "iseval", "args", "validation", "errormsg"]
        for f in expected_fields:
            macro[f]
        is_eval = macro.iseval
        self.assertTrue(is_eval == "1" or is_eval == "0")

    def test_create(self):
        self.assertTrue(self.macro_name in self.service.macros)
        self.check_macro(self.macro)

    def test_create_with_args(self):
        macro_name = testlib.tmpname() + "(1)"
        definition = '| eval value="$value$"'
        kwargs = {
            "args": "value",
            "validation": "$value$ > 10",
            "errormsg": "value must be greater than 10",
        }
        macro = self.service.macros.create(macro_name, definition=definition, **kwargs)
        self.assertTrue(macro_name in self.service.macros)
        self.check_macro(macro)
        self.assertEqual(macro.iseval, "0")
        self.assertEqual(macro.args, kwargs.get("args"))
        self.assertEqual(macro.validation, kwargs.get("validation"))
        self.assertEqual(macro.errormsg, kwargs.get("errormsg"))
        self.service.macros.delete(macro_name)

    def test_delete(self):
        self.assertTrue(self.macro_name in self.service.macros)
        self.service.macros.delete(self.macro_name)
        self.assertFalse(self.macro_name in self.service.macros)
        self.assertRaises(client.HTTPError, self.macro.refresh)

    def test_update(self):
        new_definition = '| eval updated="true"'
        self.macro.update(definition=new_definition)
        self.macro.refresh()
        self.assertEqual(self.macro["definition"], new_definition)

        is_eval = testlib.to_bool(self.macro["iseval"])
        self.macro.update(iseval=not is_eval)
        self.macro.refresh()
        self.assertEqual(testlib.to_bool(self.macro["iseval"]), not is_eval)

    def test_cannot_update_name(self):
        new_name = self.macro_name + "-alteration"
        self.assertRaises(
            client.IllegalOperationException, self.macro.update, name=new_name
        )

    def test_name_collision(self):
        opts = self.opts.kwargs.copy()
        opts["owner"] = "-"
        opts["app"] = "-"
        opts["sharing"] = "user"
        service = client.connect(**opts)
        logging.debug("Namespace for collision testing: %s", service.namespace)
        macros = service.macros
        name = testlib.tmpname()

        dispatch1 = '| eval macro_one="1"'
        dispatch2 = '| eval macro_two="2"'
        namespace1 = client.namespace(app="search", sharing="app")
        namespace2 = client.namespace(owner="admin", app="search", sharing="user")
        new_macro2 = macros.create(name, dispatch2, namespace=namespace1)
        new_macro1 = macros.create(name, dispatch1, namespace=namespace2)

        self.assertRaises(client.AmbiguousReferenceException, macros.__getitem__, name)
        macro1 = macros[name, namespace1]
        self.check_macro(macro1)
        macro1.update(**{"definition": "| eval number=1"})
        macro1.refresh()
        self.assertEqual(macro1["definition"], "| eval number=1")
        macro2 = macros[name, namespace2]
        macro2.update(**{"definition": "| eval number=2"})
        macro2.refresh()
        self.assertEqual(macro2["definition"], "| eval number=2")
        self.check_macro(macro2)

    def test_no_equality(self):
        self.assertRaises(client.IncomparableException, self.macro.__eq__, self.macro)

    def test_acl(self):
        self.assertEqual(self.macro.access["perms"], None)
        self.macro.acl_update(
            sharing="app", owner="admin", **{"perms.read": "admin, nobody"}
        )
        self.assertEqual(self.macro.access["owner"], "admin")
        self.assertEqual(self.macro.access["sharing"], "app")
        self.assertEqual(self.macro.access["perms"]["read"], ["admin", "nobody"])

    def test_acl_fails_without_sharing(self):
        self.assertRaisesRegex(
            ValueError,
            "Required argument 'sharing' is missing.",
            self.macro.acl_update,
            owner="admin",
            app="search",
            **{"perms.read": "admin, nobody"},
        )

    def test_acl_fails_without_owner(self):
        self.assertRaisesRegex(
            ValueError,
            "Required argument 'owner' is missing.",
            self.macro.acl_update,
            sharing="app",
            app="search",
            **{"perms.read": "admin, nobody"},
        )


class TestMacroSPL(testlib.SDKTestCase):
    macro_name = "SDKTestMacro"

    def setUp(self):
        testlib.SDKTestCase.setUp(self)
        self.clean()

    def tearDown(self):
        testlib.SDKTestCase.setUp(self)
        self.clean()

    def clean(self):
        for macro in self.service.macros:
            if macro.name.startswith(self.macro_name):
                self.service.macros.delete(macro.name)

    def test_use_macro_in_search(self):
        self.service.macros.create(self.macro_name, 'eval test="123"')

        stream = self.service.jobs.oneshot(
            f"| makeresults count=1 | `{self.macro_name}`",
            output_mode="json",
        )

        result = results.JSONResultsReader(stream)
        out = list(result)

        self.assertTrue(len(out) == 1)
        self.assertEqual(out[0]["test"], "123")

    def test_use_macro_in_search_with_single_arg(self):
        # Macros with arguments must contain the amount of arguments in parens,
        # otherwise a macro is not going to work.
        macro_name = self.macro_name + "(1)"

        self.service.macros.create(macro_name, 'eval test="$value$"', args="value")
        stream = self.service.jobs.oneshot(
            f"| makeresults count=1 | `{self.macro_name}(12)`",
            output_mode="json",
        )

        result = results.JSONResultsReader(stream)
        out = list(result)

        self.assertTrue(len(out) == 1)
        self.assertEqual(out[0]["test"], "12")

    def test_use_macro_in_search_with_multiple_args(self):
        # Macros with arguments must contain the amount of arguments in parens,
        # otherwise a macro is not going to work.
        macro_name = self.macro_name + "(2)"

        self.service.macros.create(
            macro_name, 'eval test="$value$", test2="$value2$"', args="value,value2"
        )
        stream = self.service.jobs.oneshot(
            f"| makeresults count=1 | `{self.macro_name}(12, 34)`",
            output_mode="json",
        )

        result = results.JSONResultsReader(stream)
        out = list(result)

        self.assertTrue(len(out) == 1)
        self.assertEqual(out[0]["test"], "12")
        self.assertEqual(out[0]["test2"], "34")

    def test_use_macro_in_search_validation_success(self):
        macro_name = self.macro_name + "(2)"

        self.service.macros.create(
            macro_name,
            'eval test="$value$", test2="$value2$"',
            args="value,value2",
            validation="value < value2",
        )

        stream = self.service.jobs.oneshot(
            f"| makeresults count=1 | `{self.macro_name}(12, 34)`",
            output_mode="json",
        )

        result = results.JSONResultsReader(stream)
        out = list(result)

        self.assertTrue(len(out) == 1)
        self.assertEqual(out[0]["test"], "12")
        self.assertEqual(out[0]["test2"], "34")

    def test_use_macro_in_search_validation_failure(self):
        macro_name = self.macro_name + "(2)"

        self.service.macros.create(
            macro_name,
            'eval test="$value$", test2="$value2$"',
            args="value,value2",
            validation="value < value2",
            errormsg="value must be smaller that value2",
        )

        def query():
            self.service.jobs.oneshot(
                f"| makeresults count=1 | `{self.macro_name}(34, 12)`",
                output_mode="json",
            )

        self.assertRaisesRegex(HTTPError, "value must be smaller that value2", query)


# This test makes sure that the endpoint we use for macros (configs/conf-macros)
# does not require admin privileges and can be used by normal users.
class TestPrivileges(testlib.SDKTestCase):
    macro_name = "SDKTestMacro"
    username = "SDKTestMacroUser".lower()
    password = "SDKTestMacroUserPassword!"

    def setUp(self):
        testlib.SDKTestCase.setUp(self)
        self.cleanUsers()

        self.service.users.create(
            username=self.username, password=self.password, roles=["user"]
        )

        self.service.logout()
        kwargs = self.opts.kwargs.copy()
        kwargs["username"] = self.username
        kwargs["password"] = self.password
        self.service = client.connect(**kwargs)

        self.cleanMacros()

    def tearDown(self):
        testlib.SDKTestCase.tearDown(self)
        self.cleanMacros()
        self.service = client.connect(**self.opts.kwargs)
        self.cleanUsers()

    def cleanUsers(self):
        for user in self.service.users:
            if user.name == self.username:
                self.service.users.delete(self.username)

    def cleanMacros(self):
        for macro in self.service.macros:
            if macro.name == self.macro_name:
                self.service.macros.delete(self.macro_name)

    def test_create_macro_no_admin(self):
        self.service.macros.create(self.macro_name, 'eval test="123"')

        stream = self.service.jobs.oneshot(
            f"| makeresults count=1 | `{self.macro_name}`",
            output_mode="json",
        )

        result = results.JSONResultsReader(stream)
        out = list(result)

        self.assertTrue(len(out) == 1)
        self.assertEqual(out[0]["test"], "123")


if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
