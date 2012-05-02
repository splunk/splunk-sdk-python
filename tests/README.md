# Splunk Test "Framework"

The truth is that there really isn't a Splunk Test Framework. It simply uses
Python's builtin unittest module.

Each distinct area of the SDK is tested in a single file. For example,
`splunk.client` is tested in `test_client.py`, while the examples are tested
in `test_examples.py`.

There are no dependencies to run the tests. You can simply execute:

    cd tests
    python -m unittest discover

or, if you have py.test installed,

    cd tests
    py.test

## Code Coverage

We have support for using the excellent `coverage.py`, which needs to be
installed on your system. You can get more information about the module
at the author's website: http://nedbatchelder.com/code/coverage/

To install it, simply use `easy_install` or `pip`:

    easy_install coverage

or

    pip install coverage

Once you have `coverage.py` installed, you can run get coverage information
as follows:

    cd tests
    coverage run runtests.py
    coverage combine
    coverage report

If you are using py.test, youcan replace 

    coverage run runtests.py 

with 

    coverage run `which py.test`

which provides better reporting, and lets you specify any additional
options, such as a particular file to test. Should you want to get an
HTML report:

    coverage html

and open `coverage_html_report/index.html` in your favorite browser.