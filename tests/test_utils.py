from __future__ import absolute_import
from tests import testlib

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


TEST_DICT = {
            'username':'admin',
            'password':'changeme',
            'port' : 8089,
            'host' : 'localhost',
            'scheme': 'https'
            }

class TestUtils(testlib.SDKTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()

    # Test dslice when a dict is passed to change key names
    def test_dslice_dict_args(self):
        args = {
            'username':'user-name', 
            'password':'new_password', 
            'port': 'admin_port', 
            'foo':'bar'
            }
        expected = {
            'user-name':'admin', 
            'new_password':'changeme', 
            'admin_port':8089
            }
        self.assertTrue(expected == dslice(TEST_DICT, args))

    # Test dslice when a list is passed
    def test_dslice_list_args(self):
        test_list = [
            'username',
            'password',
            'port',
            'host',
            'foo'
            ]
        expected = {
            'username':'admin',
            'password':'changeme',
            'port':8089,
            'host':'localhost'
            }
        self.assertTrue(expected == dslice(TEST_DICT, test_list))

    # Test dslice when a single string is passed
    def test_dslice_arg(self):
        test_arg = 'username'
        expected = {
            'username':'admin'
            }
        self.assertTrue(expected == dslice(TEST_DICT, test_arg))

    # Test dslice using all three types of arguments
    def test_dslice_all_args(self):
        test_args = [
            {'username':'new_username'},
            ['password',
            'host'],
            'port'
        ]
        expected = {
            'new_username':'admin',
            'password':'changeme',
            'host':'localhost',
            'port':8089
        }
        self.assertTrue(expected == dslice(TEST_DICT, *test_args))


if __name__ == "__main__":
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
    unittest.main()
