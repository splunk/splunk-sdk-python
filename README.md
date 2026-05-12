# Splunk Enterprise SDK for Python

[![Build Status](https://github.com/splunk/splunk-sdk-python/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/splunk/splunk-sdk-python/actions/workflows/test.yml)
![License](https://img.shields.io/badge/license-Apache%202.0-informational.svg)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B8617%2Fgithub.com%2Fsplunk%2Fsplunk-sdk-python.svg?type=small)](https://app.fossa.com/projects/custom%2B8617%2Fgithub.com%2Fsplunk%2Fsplunk-sdk-python?ref=badge_small)

The [Splunk Enterprise](https://www.splunk.com/en_us/products/splunk-enterprise.html) Software Development Kit (SDK) for Python is intended to be the primary way for developers to communicate with the Splunk platform's REST API.

You may be asking:

- [What are Splunk Apps?](https://help.splunk.com/en/splunk-enterprise/administer/admin-manual/10.0/meet-splunk-apps/apps-and-add-ons)
- [What can Splunk Apps do?](https://dev.splunk.com/enterprise/docs/developapps/extensionpoints)
- [How do I write Splunk Apps?](https://dev.splunk.com/enterprise/docs/welcome)
- [Where does the SDK fit in all this?](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/)
- What's the difference between `import splunklib` and `import splunk`?
  - This repo contains `splunklib`, whereas `splunk` is an internal library bundled with the Splunk platform.
- [How do I use AI in Splunk Apps?](splunklib/ai/README.md)

## Getting started

### Requirements

- [Python 3.13 or newer](https://www.python.org/downloads/)
- [Splunk Enterprise/Cloud](http://www.splunk.com/download)

### Installing the SDK

Using `uv`:

```python
uv init
uv add splunk-sdk
uv sync
```

If you prefer not using `uv`, using `pip` should work as expected:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install splunk-sdk
```

### Including external dependencies in your App

Because of the way Splunk Apps are built, you need to install your external dependencies to `bin/lib/` for the App to work. Then in your App script files:

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
```

### Packaging your App

An example workflow to package your App for uploading to Splunk (expect to modify it heavily):

```sh
python3 -m pip install . \
  --target bin/lib/ \
  # Needs to match the platform Splunk is built and
  # ran on, NOT the one you're writing your App on
  --platform manylinux2014_aarch64 \
  --only-binary=:all:

gtar --transform='s,^,<your_app>/,' \
  --exclude="__pycache__" \
  -czf dist/<your_app>.tgz \
  bin default

# `<your_app>.tgz` should be now ready in `dist/`!
```

[See docs](https://dev.splunk.com/enterprise/docs/developapps/createapps/appanatomy) for more details.

### Using SDK in Splunk Apps

The easiest and most effective way of learning how to use this library should be reading through the apps in our test suite, as well as the [splunk-app-examples](https://github.com/splunk/splunk-app-examples) repository. They show how to programmatically interact with the Splunk platform in a variety of scenarios - from basic metadata retrieval, one-shot searching and managing saved searches to building complete applications with modular inputs and custom search commands.

For details, see the [examples using the Splunk Enterprise SDK for Python](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/examplespython) on the Splunk Developer Portal, as well as the [Splunk Enterprise SDK for Python Reference](http://docs.splunk.com/Documentation/PythonSDK)

#### Using AI in Splunk Apps

You can now leverage AI capabilities within your Splunk Apps using the `splunklib.ai` package. Take a look at its [README](splunklib/ai/README.md) to find out how to enhance your Apps agentic behaviour, custom tools and more.

#### Connecting to a Splunk Enterprise instance

##### Using a username/password combo

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, username=<USERNAME>, password=<PASSWORD>, autologin=True)
```

##### Using a bearer token

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, splunkToken=<BEARER_TOKEN>, autologin=True)
```

##### Using a session key

```python
import splunklib.client as client

service = client.connect(host=<HOST_URL>, token=<SESSION_KEY>, autologin=True)
```

#### Creating Custom Search Commands

TODO: Link docs about this

##### Accessing instance metadata in CSCs

- The `service` metadata object is created from the `splunkd` URI and session key passed to the command invocation the search results info file and is available in `MyCommand`.`generate`/`transform`/`stream`/`reduce` methods depending on the Custom Search Command.

```python
from splunklib.searchcommands import StreamingCommand

class MyCommand(StreamingCommand):
    def get_metadata(self):
        # Access instance metadata
        service = self.service
        # Access Splunk service info
        info = service.info
        # [...]
```

##### Field retention in CSC

When working with custom search commands such as Custom Streaming Commands or Custom Generating Commands, we may need to add new fields to the records based on certain conditions. Structural changes like this may not be preserved.
If you're having issues with field retention, make sure to use `add_field(record, fieldname, value)` method from `SearchCommand` to add a new field and value to the record.

```diff
class CustomStreamingCommand(StreamingCommand):
    def stream(self, records):
        for index, record in enumerate(records):
            if index % 1 == 0:
-                record["odd_record"] = "true"
+                self.add_field(record, "odd_record", "true")
            yield record
```

##### Using a helper method to generate events properly

- Generating Custom Search Command is used to generate events using SDK code.
- Make sure to use `gen_record()` method from `SearchCommand` to add a new record and pass event data as comma-separated key=value pairs (mentioned in below example).

```diff
@Configuration()
class GeneratorTest(GeneratingCommand):
    def generate(self):
-        yield {'_time': time.time(), 'one': 1}
-        yield {'_time': time.time(), 'two': 2}
+        yield self.gen_record(_time=time.time(), one=1)
+        yield self.gen_record(_time=time.time(), two=2)

```

#### Modular Inputs Example App

[Go here](https://help.splunk.com/en/splunk-enterprise/developing-views-and-apps-for-splunk-web/10.0/modular-inputs/modular-inputs-basic-example) to find out more about setting up a Modular Input.

#### Accessing instance metadata in scripts

- The `service` metadata object is created from the `splunkd` URI and session key passed to the command invocation on the modular input stream respectively, and is available as soon as the `<script_name>.stream_events()` or `<script_name>.validate_input()` method is called.

```python
from splunklib.modularinput import Script

class MyScript(Script):
    def stream_events(self, inputs, ew):
        # Access instance metadata
        service = self.service
        # Access Splunk service info
        info = service.info
        # [...]
```

#### Accessing Modular Inputs' metadata

- In `stream_events()` you can access Modular Input app metadata from `InputDefinition` object
- See the [Modular Input App example](https://github.com/splunk/splunk-app-examples/blob/master/modularinputs/python/github_commits/bin/github_commits.py) for reference.

  ```python
  def stream_events(self, inputs, ew):
    # [...]

    # Access the modular input app's metadata (like server_host, server_uri, etc) from `InputDefinition` object
    server_host = inputs.metadata["server_host"]
    server_uri = inputs.metadata["server_uri"]
    checkpoint_dir = inputs.metadata["checkpoint_dir"]
  ```

### Contributions

We welcome all contributions!
If you would like to contribute to the SDK, see [Contributing to Splunk](https://www.splunk.com/en_us/form/contributions.html). For additional guidelines, see [CONTRIBUTING](CONTRIBUTING.md).

### Setting up a development environment

Make sure you have `uv` and `docker`/`podman` installed and available in your `$PATH`. Run `make uv-sync` to get a virtualenv set up or updated. After activating it with `source .venv/bin/activate` you should be ready to go!

#### Creating an `.env` file

To connect to Splunk Enterprise, many of the SDK examples and unit tests take command-line arguments that specify values for the host, port, and authentication. For convenience during development, you can store these arguments as key-value pairs in an `.env` file.

A file called `.env.template` exists in the root of this repository. Duplicate it as `.env`, then adjust it to your match your environment.

```sh
cp .env.template .env
```

> **WARNING:** The `.env` file isn't part of the Splunk platform. This is **not** the place for production credentials!

#### Testing

This repository contains a suite of unit and integration tests.

```sh
# Run entire test suite:
make test

# Run only the unit tests:
make test-unit
```

##### Integration tests

The integration suite requires `docker`/`podman` to work.

> NOTE: Before running the integration tests, make sure the instance of Splunk you are testing against doesn't have new events being dumped continuously into it. Several of the tests rely on a stable event count. It's best to test against a clean install of Splunk but if you can't, you should at least disable the \*NIX and Windows apps.

```sh
# This command starts a Splunk Docker container
# and waits until it reaches an operational state.
SPLUNK_VERSION=latest make docker-start

# Run the integration tests:
make test-integration
```

> Do not run the test suite against a production instance of Splunk! It will run just fine with the free Splunk license.

#### Enabling logging in `splunklib`

The default level is WARNING, which means that only events of this level and above will be visible
To change a logging level we can call setup_logging() method and pass the logging level as an argument.

> Optionally, you can also provide a custom log and date format string. When in doubt, always refer to the source code.

```python
import logging
from splunklib import setup_logging

# To see debug and above level logs
setup_logging(logging.DEBUG)
```

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

- [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools)
- [Issues and pull requests](https://github.com/splunk/splunk-sdk-python/issues/)
- [Send an e-mail to Splunk Dev Platform](mailto:devinfo@splunk.com)

## Support

- You will be granted support if you or your company are already covered under an existing maintenance/support agreement. Submit a new case in the [Support Portal](https://www.splunk.com/en_us/support-and-services.html) and include at least `Splunk Enterprise SDK for Python` in the subject line.

  If you are not covered under an existing maintenance/support agreement, you can find help through the broader community at [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

- Splunk will NOT provide support for SDKs if the core library (code in the `/splunklib` directory) has been modified. If you modify the SDK and want support, try finding it with the broader community, e.g. [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

  That said, we'd also like to know why you felt the need to modify the core library, so please send feedback and file any issues in our [GitHub Issues](https://github.com/splunk/splunk-sdk-python/issues).
