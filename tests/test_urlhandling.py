import os
from subprocess import PIPE, Popen
from os.path import expanduser
import time
import sys
import urllib
import testlib 

import splunklib.client as client
from splunklib.binding import UrlEncoded

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")

# Creates a file in the default Home directory
# Probably won't work with windows
def make_file(filename):
    Popen(("touch '%s/%s'"%(expanduser('~'),filename)), shell=True)


def delete_file(filename):
    Popen(("rm '%s/%s'"%(expanduser('~'),filename)), shell=True)


class ExamplesTestCase(testlib.SDKTestCase):
    def setUp(self):
        if os.name == "nt":
            sys.exit("Windows not supported")

        opts = parse(sys.argv[1:], config=".splunkrc")
        kwargs = dslice(opts.kwargs, FLAGS_SPLUNK)
        self.service = client.connect(**kwargs)
        super(ExamplesTestCase, self).setUp()

    def test_creating_monitor_inputs(self):
        input_names = [
            "myfile#",
            "myfile!",
            "myfile$",
            "myfile(abc).txt"
            ]
        for name in input_names:
            make_file(name)
            pathname = '/'.join([expanduser('~'), name])
            if self.service.inputs.__contains__(pathname):
                self.service.inputs.delete(name=pathname, kind="monitor")
                time.sleep(1) # Need to wait for delete to be processed or else there is a failure.
                inp = self.service.inputs.create(name=pathname, kind="monitor")
            else:
                inp = self.service.inputs.create(name=pathname, kind="monitor")
            test = self.service.inputs[pathname]
            test.refresh()
            inp.refresh()
            self.assertTrue(inp.name == pathname)
            self.assertTrue(inp.access == test.access)
            self.assertTrue(inp.content == test.content)
            self.assertTrue(inp.fields == test.fields)
            self.assertTrue(inp.links == test.links)
            self.assertTrue(inp.state == test.state)
            self.service.inputs.delete(name=pathname)
            delete_file(name)

    def test_saved_searches(self):
        search_name = [
                    "mysearch#",
                    "my/search@",
                    "my/search/test(abc)"
                    ]
        search_param = "search *"
        for search in search_name:
            if self.service.saved_searches.__contains__(search):
                service.saved_searches.delete(search)
                sear = self.service.saved_searches.create(name=search, search=search_param)
            else:
                sear = self.service.saved_searches.create(name=search, search=search_param)
            test = self.service.saved_searches[search]
            test.refresh()
            sear.refresh()
            self.assertTrue(sear.name == search)
            self.assertTrue(sear.name == test.name)
            self.assertTrue(sear.access == test.access)
            self.assertTrue(sear.content == test.content)
            self.service.saved_searches.delete(search)

    def test_urlhandling_inputs(self):
        for inp in self.service.inputs:
            raw = self.service.inputs.get(name=inp.name)
            url_name = UrlEncoded(inp.name, encode_slash=True)
            encoded = self.service.inputs.get(name=url_name)
            self.assertTrue(raw.status == encoded.status)
            self.assertTrue(raw.headers == encoded.headers)
            self.assertTrue(raw.reason == encoded.reason)
            self.assertTrue(str(raw.body)== str(encoded.body))

    def test_urlhandling_saved_searchs(self):
        for ss in self.service.saved_searches:
            raw = self.service.saved_searches.get(ss.name)
            encoded = self.service.saved_searches.get(UrlEncoded(ss.name, encode_slash=True))
            self.assertTrue(raw.status == encoded.status)
            self.assertTrue(raw.headers == encoded.headers)
            self.assertTrue(raw.reason == encoded.reason)
            self.assertTrue(str(raw.body)== str(encoded.body))

    def test_urlhandling(self):
        for inp in self.service.inputs:
            name = inp.name
            self.assertTrue(urllib.quote(name) == UrlEncoded(name))
            self.assertTrue(urllib.quote(name, '') == UrlEncoded(name, encode_slash=True))
            self.assertTrue(name == UrlEncoded(name, skip_encode=True))


if __name__=="__main__":
    os.chdir("../examples")
    try:
        import unittest2 as unittest2
    except ImportError:
        import unittest
    unittest.main()





