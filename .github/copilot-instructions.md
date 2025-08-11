# Splunk SDK Python - AI Assistant Guide

This guide helps AI coding assistants understand the key patterns and practices of the Splunk SDK for Python codebase.

## Architecture Overview

The SDK is organized into several key modules:

- `splunklib.client`: Main interface for interacting with Splunk's REST API
- `splunklib.binding`: Low-level HTTP and authentication handling
- `splunklib.data`: XML/Atom feed parsing utilities
- `splunklib.modularinput`: Framework for creating Splunk modular inputs
- `splunklib.searchcommands`: Framework for custom search commands

### Core Patterns

1. Service Connection:

```python
import splunklib.client as client
service = client.connect(
    host='localhost',
    port=8089,
    username='admin',
    password='changeme'
    # OR splunkToken=<bearer_token>
    # OR token=<session_key>
)
```

2. Resource Collections Pattern:

- All Splunk resources (apps, jobs, searches etc.) are accessed via collections
- Collections return Entity objects with attribute access
- Example:

```python
apps = service.apps
my_app = apps.create('my_app')
print(my_app['author'])  # Or: my_app.author
```

3. XML Data Handling:

- Use `splunklib.data.load()` for parsing Splunk's XML responses
- Include proper XML namespace handling as shown in `data.py`

## Development Workflows

1. Testing:

```bash
# Run all tests with Docker
make up SPLUNK_VERSION=9.2
make wait_up
make test
make down

# Run specific test
make test_specific TEST=tests/test_binding.py
```

2. Environment Setup:

- Required: Python 3.7, 3.9, or 3.13
- Create `.env` file for test credentials (see README template)
- Set `PYTHONPATH` to include SDK root

## Project-Specific Conventions

1. Search Command Development:

- Use `self.add_field(record, fieldname, value)` to modify records
- Never modify record dictionaries directly
- Example:

```python
class CustomStreamingCommand(StreamingCommand):
    def stream(self, records):
        for record in records:
            self.add_field(record, "new_field", "value")
            yield record
```

2. Modular Input Development:

- Access metadata via InputDefinition in stream_events()
- Use `gen_record()` for generating events in custom commands

## Key Integration Points

1. Authentication Methods:

- Username/password
- Bearer token
- Session key
- See connection examples in README

2. Test Dependencies:

- Requires [SDK App Collection](https://github.com/splunk/sdk-app-collection)
- Clean Splunk instance recommended (disable \*NIX/Windows apps)
- Never test against production instances

## Reference Files

- `splunklib/client.py`: Core service and entity implementations
- `splunklib/data.py`: XML parsing patterns
- `tests/README.md`: Testing configuration and practices
- `.env.template`: Environment variable template

For more details, consult the [Developer Portal Reference](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/).
