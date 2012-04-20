# The Splunk Software Development Kit for Python (Beta Release)

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

## Getting Started

In order to use the SDK you are going to need a copy of Splunk. If you don't 
already have a copy you can download one from http://www.splunk.com/download.

You can get a copy of the SDK sources by cloning into the repository with git:

> git clone https://github.com/splunk/splunk-sdk-python.git

#### Installing

You can install the Splunk SDK libraries by using `easy_install` or `pip`:

> [sudo] easy_install splunk-sdk

Or

> [sudo] pip install splunk-sdk

Alternatively, you can use `setup.py` on the sources you cloned from GitHub:

> [sudo] python setup.py install

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

    import splunklib.binding as binding

    # host defaults to localhost and port defaults to 8089
    context = binding.connect(username="admin", password="changeme")

    response = context.get('/services/authentication/users')

    print "Status: %s" % response.status
    print response.body.read()

The second layer is referred to as the _client_ layer and builds on the 
_binding_ layer to provide a friendlier interface to Splunk that abstracts 
away some of the lower level details of the _binding_ layer.

    import splunklib.client as client

    # host defaults to localhost and port defaults to 8089
    service = client.connect(username="admin", password="changeme")

    for user in service.users:
        print user.name

### Unit tests

The SDK contains a small but growing collection of unit tests. Running the
tests is simple and rewarding:

> cd tests<br>
> python runtests.py

Alternatively, you can read more about our testing "framework" 
[here](https://github.com/splunk/splunk-sdk-python/tree/master/tests).

### Layout of the repository

<table>

<tr>
<td>docs</td>
<td>Source for Sphinx based docs and build</td>
</tr>

<tr>
<td>examples</td>
<td>Examples demonstrating various SDK features</td>
<tr>

<tr>
<td>splunklib</td>
<td>Source for the Splunk library modules</td>
<tr>

<tr>
<td>tests</td>
<td>Source for unit tests</td>
<tr>

<tr>
<td>utils</td>
<td>Source for utilities shared by the examples and unit tests</td>
<tr>

</table>

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

* http://dev.splunk.com

Reference documentation for the Python SDK:

* http://splunk.github.com/splunk-sdk-python/docs/0.8.0

Reference documentation for the Splunk REST API:

* http://docs.splunk.com/Documentation/Splunk/latest/RESTAPI

Overview of Splunk and links to additional product information:

* http://docs.splunk.com/Documentation/Splunk/latest/User/SplunkOverview

## Community

Stay connected with other developers building on Splunk.

<table>

<tr>
<td><em>Email</em></td>
<td>devinfo@splunk.com</td>
</tr>

<tr>
<td><em>Issues</em>
<td><span>https://github.com/splunk/splunk-sdk-java/issues/</span></td>
</tr>

<tr>
<td><em>Answers</em>
<td><span>http://splunk-base.splunk.com/tags/java/</span></td>
</tr>

<tr>
<td><em>Blog</em>
<td><span>http://blogs.splunk.com/dev/</span></td>
</tr>

<tr>
<td><em>Twitter</em>
<td>@splunkdev</td>
</tr>

</table>

### How to contribute

If you would like to contribute to the SDK, please follow one of the links 
provided below.

* [Individual contributions](http://dev.splunk.com/goto/individualcontributions)

* [Company contributions](http://dev.splunk.com/view/companycontributions/SP-CAAAEDR)

### Support

1. You will be granted support if you or your company are already covered under an existing maintenance/support agreement. Send an email to support@splunk.com and please include the SDK you are referring to in the subject. 
2. If you are not covered under an existing maintenance/support agreement you can find help through the broader community at:
<br>Splunk answers - http://splunk-base.splunk.com/answers/ Specific tags (SDK, java, python, javascript) are available to identify your questions
<br>Splunk dev google group - http://groups.google.com/group/splunkdev
3. Splunk will NOT provide support for SDKs if the core library (this is the code in the splunklib directory) has been modified. If you modify an SDK and want support, you can find help through the broader community and Splunk answers (see above). We also want to know about why you modified the core library. You can send feedback to: devinfo@splunk.com

### Contact Us

You can reach the Dev Platform team at devinfo@splunk.com
