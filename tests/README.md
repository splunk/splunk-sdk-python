# Python SDK tests

The tests use both Python's standard **unittest** library and **pytest**, and have been tested with Python 3.7, 3.9, and 3.13. The test suite can be executed across all supported Python versions using **tox**.

## Test Types

The SDK test suite is divided into three main types:

1. [Unit Tests](./unit/)

   - Fast and isolated, do not require a running Splunk instance

2. [Integration Tests](./integration/)

   - **Require a running Splunk instance**
   - Test SDK being used to communicate with a real Splunk instance via API

3. [System Tests](./system/)
   - **Require a running Splunk instance**
   - Test SDK being used inside Splunk apps (SDK bundeled with apps inside Splunk instance)

## Setting up Splunk in Docker

Integration and system require a running test Splunk instance, which can be set up with Docker. Make sure Docker is installed and then start Splunk with:

```bash
 make up SPLUNK_VERSION=latest # runs docker compose up -d
 make wait_up # wait until the Splunk is ready
```

If running on Mac, add this line to docker-compose:

```yaml
architecture: linux/amd64
```

> **NOTE**: Before running the test suite, make sure the instance of Splunk you
> are testing against doesn't have new events being dumped continuously
> into it. Several of the tests rely on a stable event count. It's best
> to test against a clean install of Splunk, but if you can't, you
> should at least disable the \*NIX and Windows apps. **Do not run the test
> suite against a production instance of Splunk!** It will run just fine
> with the free Splunk license.

## Running tests with tox

**tox** allows running tests across multiple Python versions and environments.  
The configurations are defined in the `tox.ini` file.

- Run all tests (unit, integration, and system) on all Python versions:

  ```bash
  tox
  ```

- Run all tests (unit, integration, and system) on a specific Python versions:

  ```bash
  tox -e py39 # example for Python 3.9
  ```

- Run a specific type of tests on Python version currently active in your shell:

  ```bash
  tox -e py -- tests/unit # example for unit tests
  ```

- Run a specific type of tests on a single Python version:

  ```bash
  tox -e py37 -- tests/unit  # example for Python 3.7 unit tests
  ```

- Run a specific test file and Python version:
  ```
  tox -e py39 -- tests/unit/test_utils.py
  ```
- Run a specific test method from a specific file and Python version:
  ```
  tox -e py313 -- tests/system/test_csc_apps.py::TestEventingApp::test_metadata
  ```

## Code Coverage

Code coverage is provided via `pytest-cov`, which uses `Coverage.py` under the hood.
Coverage statistics are displayed at the end of each tox or pytest run.

## Test reports

Test reports are generated in JUnit XML format. For each tox environment, the reports are saved in: `test-reports/junit-{test-env}.xml`
