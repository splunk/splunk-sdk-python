[![Build Status](https://travis-ci.org/splunk/splunk-sdk-python.svg?branch=master)](https://travis-ci.org/splunk/splunk-sdk-python)
[![Documentation Status](https://readthedocs.org/projects/splunk-python-sdk/badge/?version=latest)](https://splunk-python-sdk.readthedocs.io/en/latest/?badge=latest)

# The Splunk Enterprise Software Development Kit for Python

#### Version 1.6.16

The Splunk Enterprise Software Development Kit (SDK) for Python contains library code and examples designed to enable developers to build applications using the Splunk platform.

The Splunk platform is a search engine and analytic environment that uses a distributed map-reduce architecture to efficiently index, search, and process large time-varying data sets.

The Splunk platform is popular with system administrators for aggregation and monitoring of IT machine data, security, compliance, and a wide variety of other scenarios that share a requirement to efficiently index, search, analyze, and generate real-time notifications from large volumes of time-series data.

The Splunk developer platform enables developers to take advantage of the same technology used by the Splunk platform to build exciting new applications.

## Getting started with the Splunk SDK for Python


## Get started with the Splunk Enterprise SDK for Python

The Splunk Enterprise SDK for Python contains library code and examples that show how to programmatically interact with the Splunk platform for a variety of scenarios including searching, saved searches, data inputs, and many more, along with building complete applications.

### Requirements

Here's what you need to get going with the Splunk Enterprise SDK for Python.

* Python 2.7+ or Python 3.7. 
  
  The Splunk Enterprise SDK for Python has been tested with Python v2.7 and v3.7.

* Splunk Enterprise

  If you haven't already installed Splunk Enterprise, download it [here](http://www.splunk.com/download). 
  For more information, see the Splunk Enterprise [_Installation Manual_](https://docs.splunk.com/Documentation/Splunk/latest/Installation).

* Splunk Enterprise SDK for Python

  Get the Splunk Enterprise SDK for Python from [PyPI](https://pypi.org/project/splunk-sdk/). If you want to contribute to the SDK, clone the repository from [GitHub](https://github.com/splunk/splunk-sdk-python).

### Install the SDK

Use the following commands to install the Splunk Enterprise SDK for Python libraries in different ways. However, it's not necessary to install the libraries to run the examples and unit tests from the SDK.

Use `easy_install`:

    [sudo] easy_install splunk-sdk

Use `pip`:

    [sudo] pip install splunk-sdk

Install the Python egg:

    [sudo] pip install --egg splunk-sdk

Install the sources you cloned from GitHub:

    [sudo] python setup.py install

## Testing Quickstart

You'll need `docker` and `docker-compose` to get up and running using this method.

```
make up SPLUNK_VERSION=8.0
make wait_up
make splunkrc_default
make test
make down
```

To run the examples and unit tests, you must put the root of the SDK on your PYTHONPATH. For example, if you downloaded the SDK to your home folder and are running OS X or Linux, add the following line to your **.bash_profile** file:

    export PYTHONPATH=~/splunk-sdk-python

The SDK command-line examples require a common set of arguments that specify the host, port, and login credentials for Splunk Enterprise. For a full list of command-line arguments, include `--help` as an argument to any of the examples.

#### Create a .splunkrc convenience file

To connect to Splunk Enterprise, many of the SDK examples and unit tests take command-line arguments that specify values for the host, port, and login credentials for Splunk Enterprise. For convenience during development, you can store these arguments as key-value pairs in a text file named **.splunkrc**. Then, the SDK examples and unit tests use the values from the **.splunkrc** file when you don't specify them.

>**Note**: Storing login credentials in the **.splunkrc** file is only for convenience during development. This file isn't part of the Splunk platform and shouldn't be used for storing user credentials for production. And, if you're at all concerned about the security of your credentials, enter them at the command line rather than saving them in this file.

To use this convenience file, create a text file with the following format:

    # Splunk Enterprise host (default: localhost)
    host=localhost
    # Splunk Enterprise admin port (default: 8089)
    port=8089
    # Splunk Enterprise username
    username=admin
    # Splunk Enterprise password
    password=changeme
    # Access scheme (default: https)
    scheme=https
    # Your version of Splunk Enterprise
    version=8.0

Save the file as **.splunkrc** in the current user's home directory.

*   For example on OS X, save the file as:

        ~/.splunkrc

*   On Windows, save the file as:

        C:\Users\currentusername\.splunkrc

    You might get errors in Windows when you try to name the file because ".splunkrc" appears to be a nameless file with an extension. You can use the command line to create this file by going to the **C:\Users\\&lt;currentusername&gt;** directory and entering the following command:

        Notepad.exe .splunkrc

    Click **Yes**, then continue creating the file.

#### Run the examples

Examples are located in the **/splunk-sdk-python/examples** directory. To run the examples at the command line, use the Python interpreter and include any arguments that are required by the example:

    python examplename.py --username="admin" --password="changeme"

If you saved your login credentials in the **.splunkrc** file, you can omit those arguments:

    python examplename.py

To get help for an example, use the `--help` argument with an example:

    python examplename.py --help

#### Run the unit tests

The Splunk Enterprise SDK for Python contains a collection of unit tests. To run them, open a command prompt in the **/splunk-sdk-python** directory and enter:

    make

You can also run individual test files, which are located in **/splunk-sdk-python/tests**. To run a specific test, enter:

    make specific_test_name

The test suite uses Python's standard library, the built-in `unittest` library, `pytest`, and `tox`.

>**Notes:**
>*  The test run fails unless the [SDK App Collection](https://github.com/splunk/sdk-app-collection) app is installed.
>*  To exclude app-specific tests, use the `make test_no_app` command.
>*  To learn about our testing framework, see [Splunk Test Suite](https://github.com/splunk/splunk-sdk-python/tree/master/tests) on GitHub.
>   In addition, the test run requires you to build the searchcommands app. The `make` command runs the tasks to do this, but more complex testing may require you to rebuild using the `make build_app` command.

## Repository

| Directory | Description                                                |
|:--------- |:---------------------------------------------------------- |
|/docs      | Source for Sphinx-based docs and build                     |
|/examples  | Examples demonstrating various SDK features                |
|/splunklib | Source for the Splunk library modules                      |
|/tests     | Source for unit tests                                      |
|/utils     | Source for utilities shared by the examples and unit tests |

### Changelog

The [CHANGELOG](CHANGELOG.md) contains a description of changes for each version of the SDK. For the latest version, see the [CHANGELOG.md](https://github.com/splunk/splunk-sdk-python/blob/master/CHANGELOG.md) on GitHub.

### Branches

The **master** branch represents a stable and released version of the SDK.
To learn about our branching model, see [Branching Model](https://github.com/splunk/splunk-sdk-python/wiki/Branching-Model) on GitHub.

## Documentation and resources

| Resource                | Description |
|:----------------------- |:----------- |
| [Splunk Developer Portal](http://dev.splunk.com) | General developer documentation, tools, and examples |
| [Integrate the Splunk platform using development tools for Python](https://dev.splunk.com/enterprise/docs/devtools/python)| Documentation for Python development |
| [Splunk Enterprise SDK for Python Reference](http://docs.splunk.com/Documentation/PythonSDK) | SDK API reference documentation |
| [REST API Reference Manual](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTprolog) | Splunk REST API reference documentation |
| [Splunk>Docs](https://docs.splunk.com/Documentation) | General documentation for the Splunk platform |
| [GitHub Wiki](https://github.com/splunk/splunk-sdk-python/wiki/) | Documentation for this SDK's repository on GitHub |


## Community

Stay connected with other developers building on the Splunk platform.

* [Email](mailto:devinfo@splunk.com)
* [Issues and pull requests](https://github.com/splunk/splunk-sdk-python/issues/)
* [Community Slack](https://splunk-usergroups.slack.com/app_redirect?channel=appdev)
* [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools)
* [Splunk Blogs](https://www.splunk.com/blog)
* [Twitter](https://twitter.com/splunkdev)

### Contributions

If you would like to contribute to the SDK, see [Contributing to Splunk](https://www.splunk.com/en_us/form/contributions.html). For additional guidelines, see [CONTRIBUTING](CONTRIBUTING.md). 

### Support

*  You will be granted support if you or your company are already covered under an existing maintenance/support agreement. Submit a new case in the [Support Portal](https://www.splunk.com/en_us/support-and-services.html) and include "Splunk Enterprise SDK for Python" in the subject line.

   If you are not covered under an existing maintenance/support agreement, you can find help through the broader community at [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

*  Splunk will NOT provide support for SDKs if the core library (the code in the <b>/splunklib</b> directory) has been modified. If you modify an SDK and want support, you can find help through the broader community and [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools). 

   We would also like to know why you modified the core library, so please send feedback to _devinfo@splunk.com_.

*  File any issues on [GitHub](https://github.com/splunk/splunk-sdk-python/issues).

### Contact Us

You can reach the Splunk Developer Platform team at _devinfo@splunk.com_.

## License

The Splunk Enterprise Software Development Kit for Python is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
