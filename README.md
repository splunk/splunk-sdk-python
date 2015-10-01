# The Splunk Software Development Kit for Python

#### Version 1.5.0

The Splunk Software Development Kit (SDK) for Python contains library code and 
examples designed to enable developers to build applications using Splunk.

Splunk is a search engine and analytic environment that uses a distributed
map-reduce architecture to efficiently index, search and process large 
time-varying data sets.

The Splunk product is popular with system administrators for aggregation and
monitoring of IT machine data, security, compliance and a wide variety of other
scenarios that share a requirement to efficiently index, search, analyze and
generate real-time notifications from large volumes of time series data.

The Splunk developer platform enables developers to take advantage of the same
technology used by the Splunk product to build exciting new applications that
are enabled by Splunk's unique capabilities.


## Getting started with the Splunk SDK for Python

The Splunk SDK for Python contains library code and examples that show how to
programmatically interact with Splunk for a variety of scenarios including 
searching, saved searches, data inputs, and many more, along with building 
complete applications. 

The information in this Readme provides steps to get going quickly, but for more
in-depth information be sure to visit the 
[Splunk Developer Portal](http://dev.splunk.com/view/SP-CAAAEBB). 
### Requirements

Here's what you need to get going with the Splunk SDK for Python.

#### Python

The Splunk SDK for Python requires Python 2.6+. 

#### Splunk

If you haven't already installed Splunk, download it 
[here](http://www.splunk.com/download). For more about installing and running 
Splunk and system requirements, see 
[Installing & Running Splunk](http://dev.splunk.com/view/SP-CAAADRV). 

#### Splunk SDK for Python
Get the Splunk SDK for Python; [download the SDK as a ZIP](http://dev.splunk.com/view/SP-CAAAEBB) 
and extract the files. Or, if you want to contribute to the SDK, clone the 
repository from [GitHub](https://github.com/splunk/splunk-sdk-python).


### Installing the SDK

You can install the Splunk SDK for Python libraries by using `easy_install` or `pip`:

    [sudo] easy_install splunk-sdk

Or

    [sudo] pip install splunk-sdk

Or to install the Python egg

    [sudo] pip install --egg splunk-sdk

Alternatively, you can use **setup.py** on the sources you cloned from GitHub:

    [sudo] python setup.py install

However, it's not necessary to install the libraries to run the
examples and unit tests from the SDK.


### Running the examples and unit tests

To run the examples and unit tests, you must put the root of
the SDK on your PYTHONPATH. For example, if you have downloaded the SDK to your
home folder and are running OS X or Linux, add the following line to your
**.bash_profile**:

    export PYTHONPATH=~/splunk-sdk-python

The SDK command-line examples require a common set of arguments
that specify things like the Splunk host, port, and login credentials. For a 
full list of command-line arguments, include `--help` as an argument to any of 
the examples. 

#### .splunkrc

To connect to Splunk, many of the SDK examples and unit tests take command-line
arguments that specify values for the host, port, and login credentials for
Splunk. For convenience during development, you can store these arguments as
key-value pairs in a text file named **.splunkrc**. Then, the SDK examples and 
unit tests use the values from the **.splunkrc** file when you don't specify 
them.

To use this convenience file, create a text file with the following format:

    # Splunk host (default: localhost)
    host=localhost
    # Splunk admin port (default: 8089)
    port=8089
    # Splunk username
    username=admin
    # Splunk password
    password=changeme
    # Access scheme (default: https)
    scheme=https
    # Your version of Splunk (default: 5.0)
    version=5.0

Save the file as **.splunkrc** in the current user's home directory.

*   For example on OS X, save the file as: 

        ~/.splunkrc

*   On Windows, save the file as: 

        C:\Users\currentusername\.splunkrc

    You might get errors in Windows when you try to name the file because
    ".splunkrc" looks like a nameless file with an extension. You can use
    the command line to create this file&mdash;go to the 
    **C:\Users\currentusername** directory and enter the following command: 

        Notepad.exe .splunkrc

    Click **Yes**, then continue creating the file.

**Note**: Storing login credentials in the **.splunkrc** file is only for 
convenience during development. This file isn't part of the Splunk platform and 
shouldn't be used for storing user credentials for production. And, if you're 
at all concerned about the security of your credentials, just enter them at 
the command line rather than saving them in this file. 


#### Examples

Examples are located in the **/splunk-sdk-python/examples** directory. To run 
the examples at the command line, use the Python interpreter and include any 
arguments that are required by the example:

    python examplename.py --username="admin" --password="changeme"

If you saved your login credentials in the **.splunkrc** file, you can omit 
those arguments:

    python examplename.py

To get help for an example, use the `--help` argument with an example:

    python examplename.py --help

#### Unit tests

The Splunk SDK for Python contains a collection of unit tests. To run them, open a 
command prompt in the **/splunk-sdk-python** directory and enter:

    python setup.py test

You can also run individual test files, which are located in 
**/splunk-sdk-python/tests**. For example, to run the apps test, open a command 
prompt in the **/splunk-sdk-python/tests** subdirectory and enter:

    python test_app.py

The test suite uses Python's standard library and the built-in `unittest` 
library. If you're using Python 2.7, you're all set. However, if you are using 
Python 2.6, you'll also need to install the `unittest2` library to
get the additional features that were added to Python 2.7.

You can read more about our testing framework on
[GitHub](https://github.com/splunk/splunk-sdk-python/tree/master/tests).

## Repository

<table>

<tr>
<td><b>/docs</b></td>
<td>Source for Sphinx-based docs and build</td>
</tr>

<tr>
<td><b>/examples</b></td>
<td>Examples demonstrating various SDK features</td>
<tr>

<tr>
<td><b>/splunklib</b></td>
<td>Source for the Splunk library modules</td>
<tr>

<tr>
<td><b>/tests</b></td>
<td>Source for unit tests</td>
<tr>

<tr>
<td><b>/utils</b></td>
<td>Source for utilities shared by the examples and unit tests</td>
<tr>

</table>

### Changelog

The **CHANGELOG.md** file in the root of the repository contains a description
of changes for each version of the SDK. You can also find it online at 
[https://github.com/splunk/splunk-sdk-python/blob/master/CHANGELOG.md](https://github.com/splunk/splunk-sdk-python/blob/master/CHANGELOG.md).

### Branches

The **master** branch always represents a stable and released version of the SDK.
You can read more about our branching model on our Wiki at 
[https://github.com/splunk/splunk-sdk-python/wiki/Branching-Model](https://github.com/splunk/splunk-sdk-python/wiki/Branching-Model).

## Documentation and resources
If you need to know more: 

* For all things developer with Splunk, your main resource is the 
  [Splunk Developer Portal](http://dev.splunk.com).

* For conceptual and how-to documentation, see the 
  [Overview of the Splunk SDK for Python](http://dev.splunk.com/view/SP-CAAAEBB).

* For API reference documentation, see the 
  [Splunk SDK for Python Reference](http://docs.splunk.com/Documentation/PythonSDK).

* For more about the Splunk REST API, see the 
  [REST API Reference](http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI).

* For more about about Splunk in general, see 
  [Splunk>Docs](http://docs.splunk.com/Documentation/Splunk).

* For more about this SDK's repository, see our 
  [GitHub Wiki](https://github.com/splunk/splunk-sdk-python/wiki/).

## Community

Stay connected with other developers building on Splunk.

<table>

<tr>
<td><b>Email</b></td>
<td>devinfo@splunk.com</td>
</tr>

<tr>
<td><b>Issues</b>
<td><span>https://github.com/splunk/splunk-sdk-python/issues/</span></td>
</tr>

<tr>
<td><b>Answers</b>
<td><span>http://splunk-base.splunk.com/tags/python/</span></td>
</tr>

<tr>
<td><b>Blog</b>
<td><span>http://blogs.splunk.com/dev/</span></td>
</tr>

<tr>
<td><b>Twitter</b>
<td>@splunkdev</td>
</tr>

</table>

### How to contribute

If you would like to contribute to the SDK, go here for more information:

* [Splunk and open source](http://dev.splunk.com/view/opensource/SP-CAAAEDM)

* [Individual contributions](http://dev.splunk.com/goto/individualcontributions)

* [Company contributions](http://dev.splunk.com/view/companycontributions/SP-CAAAEDR)

### Support

1. You will be granted support if you or your company are already covered 
   under an existing maintenance/support agreement. Send an email to 
   _support@splunk.com_ and include "Splunk SDK for Python" in the subject line. 

2. If you are not covered under an existing maintenance/support agreement, you 
   can find help through the broader community at:

   <ul>
   <li><a href='http://splunk-base.splunk.com/answers/'>Splunk Answers</a> (use 
    the <b>sdk</b>, <b>java</b>, <b>python</b>, and <b>javascript</b> tags to 
    identify your questions)</li>
   <li><a href='http://groups.google.com/group/splunkdev'>Splunkdev Google 
    Group</a></li>
   </ul>
3. Splunk will NOT provide support for SDKs if the core library (the 
   code in the <b>/splunklib</b> directory) has been modified. If you modify an 
   SDK and want support, you can find help through the broader community and 
   Splunk answers (see above). We would also like to know why you modified the 
   core library&mdash;please send feedback to _devinfo@splunk.com_.
4. File any issues on 
   [GitHub](https://github.com/splunk/splunk-sdk-python/issues).

### Contact Us

You can reach the Developer Platform team at _devinfo@splunk.com_.

## License

The Splunk Software Development Kit for Python is licensed under the Apache
License 2.0. Details can be found in the file LICENSE.

For compatibility with Python 2.6, The Splunk Software Development Kit
for Python ships with ordereddict.py from the ordereddict package on
[PyPI](http://pypi.python.org/pypi/ordereddict/1.1), which is licensed
under the MIT license (see the top of splunklib/ordereddict.py).
