# Splunk Test "Framework"

The truth is that there really isn't a Splunk Test Framework. It simply uses
Python's builtin unittest module.

Each distinct area of the SDK is tested in a single file. For example,
roles are tested in `test_role.py`, while the examples are tested
in `test_examples.py`.

Before running the test suite, make sure the instance of Splunk you
are testing against doesn't have new events being dumped continuously
into it. Several of the tests rely on a stable event count. It's best
to test against a clean install of Splunk, but if you cannot, you
should at least disable the *NIX and Windows apps. Do not run the test
suite against a production instance of Splunk! It will run just fine
with the free Splunk license, so don't be stingy with instances.

You also need to install the `sdk-app-collection` app in your instance of
Splunk. The `sdk-app-collection` is a set of small, single purpose apps
for testing capabilities that cannot be created with the REST API.You can
fetch it from `https://github.com/splunk/sdk-app-collection`. Put the
whole repository in `$SPLUNK_HOME/etc/apps`, so the git root would be
`$SPLUNK_HOME/etc/apps/sdk-app-collection`.

The test suite depends on nothing but Python's standard library. You can
simply execute:

    python setup.py test

or run the test_all.py script in the tests/ directory.

## Code Coverage

We have support for using the excellent `coverage.py`, which needs to be
installed on your system. You can get more information about the module
at the author's website: http://nedbatchelder.com/code/coverage/

To install it, simply use `easy_install` or `pip`:

    pip install coverage

or

    easy_install coverage

Once you have `coverage.py` installed, you can run get coverage information
as follows:

    python setup.py coverage

This will create an HTML report in coverage_html/. Open `coverage_html/index.html`
in your favorite browser to see the coverage report.