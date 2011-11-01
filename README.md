# The Splunk Software Development Kit for Python (Preview Release)

This SDK contains library code and examples designed to enable developers to
build applications using Splunk.

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


## License

The Splunk Software Development Kit for Python is licensed under the Apache
License 2.0. Details can be found in the file LICENSE.

## This SDK is a Preview Release

1.  This Preview release a pre-beta release.  There will also be a beta release 
    prior to a general release.  It is incomplete and may have bugs.

2.  The Apache license only applies to the SDK and no other Software provided 
    by Splunk.

3.  Splunk in using the Apache license is not providing any warranties, 
    indemnification or accepting any liabilities  with the Preview SDK.

4.  Splunk is not accepting any Contributions to the Preview release of the SDK.  
    All Contributions during the Preview SDK will be returned without review.

## Getting Started

In order to use the SDK you are going to need a copy of Splunk. If you don't 
already have a copy you can download one from http://www.splunk.com/download.

You can get a copy of the SDK sources by cloning into the repository with git:

    git clone https://github.com/splunk/splunk-sdk-python.git

#### Installing

You can install the Splunk SDK libraries by using `easy_install` or `pip`:

    [sudo] easy_install splunk-sdk

Or

    [sudo] pip install splunk-sdk

Alternatively, you can use `setup.py` on the sources you cloned from GitHub:

    [sudo] python setup.py install

However, it's not necessarry to install the libraries in order to run the
examples and unit tests from the SDK.

#### Requirements

The SDK requires Python 2.6+. 

#### Running the examples and units

In order to run the Splunk examples and unit tests, you must put the root of
the SDK on your PYTHONPATH.

The SDK command line examples require a common set of command line arguments
that specify things like the Splunk host and port and login credentials. You
can get a full list of command line arguments by typing `--help` as an argument
to any of the command line examples. 

#### .splunkrc

The examples and units are also desigend to receive arguments from an optional
`.splunkrc` file located in your home directory. The format of the file is
simply a list of key=value pairs, same as the options that are taken on the
command line, for example:

    host=localhost
    username=admin
    password=changeme

The `.splunkrc` file is a feature of the SDK examples and unit tests and not
the Splunk platform or SDK libraries and is intended simply as convenience for
developers using the SDK. 

The `.splunkrc` file should not be used for storing user credentials for apps
built on Splunk and should not be used if you are concerned about the security
of the credentails used in your development environment.

You can view a sample `.splunkrc` file by looking at the `splunkrc.spec` file
in the root directory of the repistory.

## Overview

The Splunk developer platform consists of three primary components: `splunkd`, 
the engine, `splunkweb`, the app framework that sits on top of the engine,
and the Splunk SDKs that interface with the REST API.

This SDK enables developers to target `splunkd` by making calls against the
engine's REST API and by accessing the various `splunkd` extension points such
as custom search commands, lookup functions, scripted inputs and custom REST
handlers.

You can find additional information about building applications on Splunk at 
our developer portal at http://dev.splunk.com. 

### Hello Splunk

The Splunk library included in this SDK consists of two layers of API that 
can be used to interact with splunkd. The lower layer is referred to as the
_binding_ layer. It is a thin wrapper around low-level HTTP capabilities, 
including:

* A pluggable HTTP component that can be user-supplied.
* Handles authentication and namespace URL management
* Accessible low-level HTTP interface for use by developers who want
    to be close to the wire.

You can see an example use of the library here:

    import splunk.binding as binding

    # host defaults to localhost and port defaults to 8089
    context = binding.connect(username="admin", password="changeme")

    response = context.get('/services/authentication/users')

    print "Status: %s" % response.status
    print response.body.read()

The second layer is referred to as the _client_ layer and builds on the 
_binding_ layer to provide a friendlier interface to Splunk that abstracts 
away some of the lower level details of the _binding_ layer.

    from pprint import pprint

    import splunk.client as client

    # host defaults to localhost and port defaults to 8089
    service = client.connect(username="admin", password="changeme")

    for user in service.users:
        pprint(user())

### Unit tests

The SDK contains a small but growing collection of unit tests. Running the
tests is simple and rewarding:

    cd tests
    ./runtests.py

Alternatively, you can read more about our testing "framework" 
[here](https://github.com/splunk/splunk-sdk-python/tree/master/tests).

### Layout of the repository

<dl>
<dt>./docs</dt>
<dd>Contains a few detailed notes specific to the SDK. In general documentation
    about developing on Splunk can be found on dev.splunk.com.</dd>
<dt>./examples</dt>
<dd>Contains s variety of Splunk samples demonstrating the various library
    modules.</dd>
<dt>./splunk</dt>
<dd>The Splunk library modules.</dd>
<dt>./tests</dt>
<dd>The SDK unit tests.</dd>
<dt>./utils</dt>
<dd>Generic utility code shared by the examples and unit tests.</dd>
</dl>

### Changelog

You can look at the changelog for each version 
[here](https://github.com/splunk/splunk-sdk-python/blob/master/CHANGELOG.md)

### Branches

The `master` branch always represents a stable and released version of the SDK.
You can read more about our branching model on our 
[Wiki](https://github.com/splunk/splunk-sdk-python/wiki/Branching-Model).

## Resources

You can find anything having to do with developing on Splunk at the Splunk
developer portal:

*   http://dev.splunk.com

You can also find full reference documentation of the REST API:

*   http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI

For a gentle introduction to the Splunk product and some of its capabilities:

*   http://docs.splunk.com/Documentation/Splunk/latest/User/SplunkOverview

## Community

* Email: Stay connected with other developers building on Splunk: devinfo@splunk.com
* Issues: https://github.com/splunk/splunk-sdk-python/issues
* Answers: Check out this tag on Splunk answers for:  
    http://splunk-base.splunk.com/tags/python/
* Blog:  http://blogs.splunk.com/dev/
* Twitter: [@splunkdev](http://twitter.com/#!/splunkdev)

### How to contribute

We aren't ready to accept code contributions yet, but will be shortly.  Check 
this README for more updates soon.

### Support

* SDKs in Preview will not be Splunk supported.  Once the Python SDK moves to 
an Open Beta we will provide more detail on support.  

* Issues should be filed here:  https://github.com/splunk/splunk-sdk-python/issues

### Contact Us
You can reach the Dev Platform team at devinfo@splunk.com
