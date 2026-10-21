# Contributing Guidelines

## How to contribute

If you would like to contribute to this project, see [Contributions to Splunk](https://www.splunk.com/en_us/form/contributions.html) for more information.

## Issues and bug reports

If you're seeing some unexpected behavior with this project, please create an [issue](https://github.com/splunk/splunk-sdk-python/issues) on GitHub with the following information:

1. Version of this project you're using (ex: 1.5.0)
2. Platform version (ex: Windows Server 2012 R2)
3. Framework version (ex: Python 3.7)
4. Splunk Enterprise version (ex: 9.0)
5. Other relevant information (ex: local/remote environment, Splunk network configuration, standalone or distributed deployment, are load balancers used)

Alternatively, if you have a Splunk question please ask on [Splunk Answers](https://community.splunk.com/t5/Splunk-Development/ct-p/developer-tools).

## Pull requests

We love to see pull requests!

To create a pull request:

1. Fill out the [Individual Contributor Agreement](https://www.splunk.com/en_us/form/contributions.html).
2. Fork the [repository](https://github.com/splunk/splunk-sdk-python).
3. Make changes to the **develop** branch, preferably with tests.
4. Create a [pull request](https://github.com/splunk/splunk-sdk-python/pulls) against the **develop** branch.

## Development guidelines

See [AGENTS.md](AGENTS.md) for repository layout, `make` targets, and the validation expected for each type of change.

### Coding style, rules & naming conventions

- Python 3.13+.
- Ruff is the linter/formatter. isort is configured with `combine-as-imports = true`.
- Type checking uses `basedpyright`.
- Naming follows PEP 8 and is enforced by ruff's pep8-naming (`N`) rules. Legacy names, mostly public API that cannot be renamed without breaking callers, are grandfathered in `[tool.ruff.lint.pep8-naming] extend-ignore-names` in `pyproject.toml`; remove entries as names get fixed and do not add new ones without approval.
- Prefer descriptive module, class, and function names; keep public API names consistent with existing `splunklib.*` patterns.
- Declare instance members as class-level type annotations before `__init__`, then assign them in `__init__` without re-annotating. This matches the pattern used throughout `splunklib/ai/`.
- Docstrings should be concise and actionable.
- Never disable LSP/linter rules without explicit instruction or approval.
- New code must not introduce new `basedpyright`/`ruff` errors or warnings, or regressions in tests.
- Never modify `.basedpyright/baseline.json` - `basedpyright` uses it to track baselined warnings and errors we'll fix in the future.

### Writing style

Be concise and direct.
Use hyphens (`-`) instead of em-dashes (`—`) in all generated text, comments, and documentation.

### Dead code

The SDK does not rely on any dead code detection, since it is held to a backwards-compatibility contract:
public API surface (classes, functions, methods) can appear unused within this repo while still being consumed
by external callers. Do not remove code solely because it looks unreferenced internally - check whether it's
part of the public API first.

## Contact us

If you have a paid Splunk Enterprise or Splunk Cloud license, you can contact [Support](https://www.splunk.com/en_us/support-and-services.html) with questions.

You can reach the Splunk Developer Platform team at _devinfo@splunk.com_.
