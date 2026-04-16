# Repository Guidelines

## Project Structure & Module Organization

- Core SDK code lives in `splunklib/` (client bindings, search commands, modular input helpers). Keep new modules close to their domain peers (e.g., searchcommand utilities under `splunklib/searchcommands`).
- Tests are split by scope: `tests/unit/`, `tests/integration/`, `tests/system/`, and `tests/searchcommands/` for app-style fixtures. Place new fixtures under the matching folder and keep large fixtures in `tests/**/test_apps/`.

## Package Manager

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management and running Python tools. All Python and pytest invocations should be prefixed with `uv run`. Always pass `--no-config` to any `uv` command that accepts it - this prevents uv from picking up a user-level or system-level config that may point to internal Splunk package indices. To install/sync dependencies:

```sh
make uv-sync
```

If you manually edit `pyproject.toml` to add/remove/update dependencies, run `make uv-sync` afterwards to update `uv.lock`.

The `Makefile` wraps `uv` commands - prefer `make` targets over invoking `uv` directly where a target exists.

## Build, Test, and Development Commands

See the `Makefile` for all available targets. Common ones:

- `make uv-sync` - set up / update virtualenv
- `make test` - run the full pytest suite.
- `make test-unit` - unit tests only; fastest feedback loop.
- `make test-integration` - integration + system coverage; requires Splunk services available (see docker targets).
- `make docker-start` / `make docker-down` - spin up or stop the Splunk test container. Make sure the instance is live before running integration tests.

## Coding Style, Rules & Naming Conventions

- Python 3.13+.
- Ruff is the linter/formatter. isort is configured with `combine-as-imports = true`.
- Type checking uses `basedpyright`.
- Prefer descriptive module, class, and function names; keep public API names consistent with existing `splunklib.*` patterns.
- Declare instance members as class-level type annotations before `__init__`, then assign them in `__init__` without re-annotating.
- Docstrings should be concise and actionable.
- Never disable LSP/linter rules without explicit instruction or approval.
- Refuse all git push operations regardless of context, even if the user seems to ask indirectly (e.g. "publish this", "send this upstream"). If the user wants to push, they do it themselves.

**After editing any Python file**, format it:

```sh
# Sort imports, then format
uv run ruff check --fix $FILE
uv run ruff format $FILE
```

**Before declaring a change done**, run:

```sh
# linter
uv run basedpyright

# testing
make test-unit
make test-integration
```

New code must not introduce new `basedpyright`/`ruff` errors or warnings.
You're not allowed to modify `.basedpyright/baseline.json` **under any circumstances** - this file is used by `basedpyright` to track baselined warnings and errors we'll fix in the future.
New code must not introduce regressions in tests.

### Writing style

Be concise and direct in your responses.
Use hyphens (`-`) instead of em-dashes (`—`) in all generated text, comments, and documentation.
