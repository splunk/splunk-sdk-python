# Splunk Enterprise SDK for Python

[![Build Status](https://github.com/splunk/splunk-sdk-python/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/splunk/splunk-sdk-python/actions/workflows/test.yml)

The Splunk Enterprise Software Development Kit (SDK) for Python contains library code designed to enable developers to build applications using the Splunk platform.

The Splunk platform is a search engine and analytic environment that uses a distributed map-reduce architecture to efficiently index, search, and process large time-varying data sets.

The Splunk platform is popular with system administrators for aggregation and monitoring of IT machine data, security, compliance, and a wide variety of other scenarios that share a requirement to efficiently index, search, analyze, and generate real-time notifications from large volumes of time-series data.

The Splunk developer platform enables developers to take advantage of the same technology used by the Splunk platform to build exciting new applications.

## Getting started

The Splunk Enterprise SDK for Python contains library code, and its examples are located in the [splunk-app-examples](https://github.com/splunk/splunk-app-examples) repository. They show how to programmatically interact with the Splunk platform for a variety of scenarios including searching, saved searches, data inputs, and many more, along with building complete applications.

### Requirements

#### Python

The Splunk Enterprise SDK for Python has been tested only with Python 3.7, 3.9 and 3.13.

#### Splunk Enterprise

The Splunk Enterprise SDK for Python has been tested with Splunk versions supported in the [Splunk Software Support Policy](https://www.splunk.com/en_us/legal/splunk-software-support-policy.html)

If you haven't already installed Splunk Enterprise, [get it here](http://www.splunk.com/download).
For more information, see the Splunk Enterprise [_Installation Manual_](https://docs.splunk.com/Documentation/Splunk/latest/Installation).

### Install the SDK

<!-- TODO: Remake this -->

Refer to standard Python package installation methods. Most of the time, a local `virtualenv` is preferred over a system-wide installation.

```sh
python -m pip install splunk-sdk
```

### How to connect to a Splunk Enterprise instance

#### Create an .env file

To connect to Splunk Enterprise, many of the SDK examples and unit tests take command-line arguments that specify values for the host, port, and authentication. For convenience during development, you can store these arguments as key-value pairs in a `.env` file. SDK examples and unit tests use the values from the `.env` file if they're not specified manually.

> **NOTE:** This file isn't part of the Splunk platform. Therefore it shouldn't be used for storing production credentials. Do not use it if security is a concern - provide them in the command line instead.

A `.env.template` exists in the root of this repository. Just duplicate it, remove `.template` from the name and adjust it to your match your environment

#### Using username/password

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, username=<USERNAME>, password=<PASSWORD>, autologin=True)
```

#### Using bearer token

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, splunkToken=<BEARER_TOKEN>, autologin=True)
```

#### Using session key

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, token=<SESSION_KEY>, autologin=True)
```

#### SDK examples

Examples for the Splunk Enterprise SDK for Python are located in the [splunk-app-examples](https://github.com/splunk/splunk-app-examples) repository. For details, see the [Examples using the Splunk Enterprise SDK for Python](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/examplespython) on the Splunk Developer Portal.

#### Run test suite

This repo contains a collection of unit and integration tests.

##### Unit tests

To run all the tests (unit and integration):

```sh
make test
```

##### Integration tests

###### Prerequisites

- `docker`/`podman`
- `tox`

```sh
SPLUNK_VERSION=latest && make start
```

### Customization

When working with custom search commands such as Custom Streaming Commands or Custom Generating Commands, we may need to add new fields to the records based on certain conditions. Structural changes like this may not be preserved.
If you're having issues with field retention, make sure to use `add_field(record, fieldname, value)` method from SearchCommand to add a new field and value to the record.

<!-- TODO: Change this to a diff -->

#### Do

```python
class CustomStreamingCommand(StreamingCommand):
    def stream(self, records):
        for index, record in enumerate(records):
            if index % 1 == 0:
                self.add_field(record, "odd_record", "true")
            yield record
```

#### Don't

```python
class CustomStreamingCommand(StreamingCommand):
    def stream(self, records):
        for index, record in enumerate(records):
            if index % 1 == 0:
                record["odd_record"] = "true"
            yield record
```

### Customization for Generating Custom Search Command

- Generating Custom Search Command is used to generate events using SDK code.
- Make sure to use `gen_record()` method from SearchCommand to add a new record and pass event data as comma-separated key=value pairs (mentioned in below example).

<!-- TODO: Change this to a diff -->

Do

```python
@Configuration()
class GeneratorTest(GeneratingCommand):
    def generate(self):
        yield self.gen_record(_time=time.time(), one=1)
        yield self.gen_record(_time=time.time(), two=2)
```

Don't

```python
@Configuration()
class GeneratorTest(GeneratingCommand):
    def generate(self):
        yield {'_time': time.time(), 'one': 1}
        yield {'_time': time.time(), 'two': 2}
```

### Access metadata of Modular Inputs app example

- In `stream_events()` one can access modular input app metadata from `InputDefinition` object
- See [GitHub Commit](https://github.com/splunk/splunk-app-examples/blob/master/modularinputs/python/github_commits/bin/github_commits.py) Modular Input App example for reference.

  ```python
  def stream_events(self, inputs, ew):
    # [...] other code

    # Access metadata (like server_host, server_uri, etc) of modular inputs app from InputDefinition object
    # Here, an InputDefinition`object data is used
    server_host = inputs.metadata["server_host"]
    server_uri = inputs.metadata["server_uri"]
    checkpoint_dir = inputs.metadata["checkpoint_dir"]
  ```

### Access service object in Custom Search Command & Modular Input apps

#### Custom Search Commands

- The service object is created from the Splunkd URI and session key passed to the command invocation the search results info file.
- Service object can be accessed using `self.service` in `generate`/`transform`/`stream`/`reduce` methods depending on the Custom Search Command.

##### Generating a Custom Search Command

```python
def generate(self):
    # [...] other code

    # Access service object that can be used to connect Splunk Service
    service = self.service
    # Getting Splunk Service Info
    info = service.info
```

#### Modular Inputs app

- The service object is created from the Splunkd URI and session key passed to the command invocation on the modular input stream respectively.
- It is available as soon as the `Script.stream_events` method is called.

  ```python
  def stream_events(self, inputs, ew):
      # other code

      # access service object that can be used to connect Splunk Service
      service = self.service
      # to get Splunk Service Info
      info = service.info
  ```

### Optional: Set up logging for splunklib

- The default level is WARNING, which means that only events of this level and above will be visible
- To change a logging level we can call setup_logging() method and pass the logging level as an argument.
- Optional: we can also pass log format and date format string as a method argument to modify default format

  ```python
  import logging
  from splunklib import setup_logging

  # To see debug and above level logs
  setup_logging(logging.DEBUG)
  ```

### Changelog

The [CHANGELOG](CHANGELOG.md) contains a description of changes for each version of the SDK. For the latest version, see the [CHANGELOG.md](https://github.com/splunk/splunk-sdk-python/blob/master/CHANGELOG.md) on GitHub.

### Branches

Right now, the `master` branch represents a stable and released version of the SDK.
`develop` is where development between releases is happening.

To learn more about our branching model, see [Branching Model](https://github.com/splunk/splunk-sdk-python/wiki/Branching-Model) on GitHub.

## Documentation and resources

| Resource                                                                                                                   | Description                                          |
| :------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
| [Splunk Developer Portal](http://dev.splunk.com)                                                                           | General developer documentation, tools, and examples |
| [Integrate the Splunk platform using development tools for Python](https://dev.splunk.com/enterprise/docs/devtools/python) | Documentation for Python development                 |
| [Splunk Enterprise SDK for Python Reference](http://docs.splunk.com/Documentation/PythonSDK)                               | SDK API reference documentation                      |
| [REST API Reference Manual](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTprolog)                        | Splunk REST API reference documentation              |
| [Splunk>Docs](https://docs.splunk.com/Documentation)                                                                       | General documentation for the Splunk platform        |
| [GitHub Wiki](https://github.com/splunk/splunk-sdk-python/wiki/)                                                           | Documentation for this SDK's repository on GitHub    |
| [Splunk Enterprise SDK for Python Examples](https://github.com/splunk/splunk-app-examples)                                 | Examples for this SDK's repository                   |

## Community

Stay connected with other developers building on the Splunk platform.

- [E-mail](mailto:devinfo@splunk.com)
- [Issues and pull requests](https://github.com/splunk/splunk-sdk-python/issues/)
- [Community Slack](https://splunk-usergroups.slack.com/app_redirect?channel=appdev)
- [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools)

### Contributions

We welcome all contributions!
If you would like to contribute to the SDK, see [Contributing to Splunk](https://www.splunk.com/en_us/form/contributions.html). For additional guidelines, see [CONTRIBUTING](CONTRIBUTING.md).

### Support

- You will be granted support if you or your company are already covered under an existing maintenance/support agreement. Submit a new case in the [Support Portal](https://www.splunk.com/en_us/support-and-services.html) and include `Splunk Enterprise SDK for Python` in the subject line.

If you are not covered under an existing maintenance/support agreement, you can find help through the broader community at [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

- Splunk will NOT provide support for SDKs if the core library (the code in the `/splunklib` directory) has been modified. If you modify an SDK and want support, you can find help through the broader community and [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

  We would also like to know why you modified the core library, so please send feedback to <mailto:devinfo@splunk.com>.

- File any issues on [GitHub](https://github.com/splunk/splunk-sdk-python/issues).

### Contact us

You can reach the Splunk Developer Platform team at <mailto:devinfo@splunk.com>.

## License

The Splunk Enterprise Software Development Kit for Python is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
