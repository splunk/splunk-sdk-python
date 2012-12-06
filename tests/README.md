# Splunk Test Suite

The test suite uses Python's standard library and the built-in **unittest** 
library. If you're using Python 2.7, you're all set. However, if you are using 
Python 2.6, you'll also need to install the **unittest2** library to get the 
additional features that were added to Python 2.7 (just run `pip install 
unittest2` or `easy_install unittest2`).

To run the unit tests, open a command prompt in the **/splunk-sdk-python** 
directory and enter:

    python setup.py test

You can also run individual test files, which are located in 
**/splunk-sdk-python/tests**. Each distinct area of the SDK is tested in a 
single file. For example, roles are tested
in `test_role.py`. To run this test, open a command prompt in
the **/splunk-sdk-python/tests** subdirectory and enter:

    python test_role.py

NOTE: Before running the test suite, make sure the instance of Splunk you
are testing against doesn't have new events being dumped continuously
into it. Several of the tests rely on a stable event count. It's best
to test against a clean install of Splunk, but if you can't, you
should at least disable the *NIX and Windows apps. Do not run the test
suite against a production instance of Splunk! It will run just fine
with the free Splunk license.


## Code Coverage

Coverage.py is an excellent tool for measuring code coverage of Python programs.

To install it, use easy_install:

    easy_install coverage

Or use pip:

    pip install coverage

To generate a report of the code coverage of the unit test suite, open a command
prompt in the **/splunk-sdk-python** directory and enter:

    python setup.py coverage

This command runs the entire test suite and writes an HTML coverage report to 
the **/splunk-sdk-python/coverage_report** directory.

For more information about Coverage.py, see the author's website 
([http://nedbatchelder.com/code/coverage/](http://nedbatchelder.com/code/coverage/)).