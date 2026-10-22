# Repository Guidelines

## Routing

- `splunklib/` - core SDK code (client bindings, `splunklib/searchcommands/`, `splunklib/modularinput/`); keep new modules next to their domain peers.
- `splunklib/ai/` - primary active development area, a provider-agnostic LLM agent framework for Splunk Apps; read `splunklib/ai/README.md` for its architecture, supported models, and usage before changing it.
- `docs/` - Sphinx API reference (`.rst`); update it when changing or documenting public SDK modules.
- `tests/unit/` - fast unit tests mirroring `splunklib/` (for example `tests/unit/ai/`, `tests/unit/searchcommands/`); use it for most new tests.
- `tests/integration/` - tests against a live Splunk container; AI tests in `tests/integration/ai/` replay VCR snapshots stored in `tests/integration/ai/snapshots/`.
- `tests/system/test_apps/` - Splunk test apps mounted by `compose.yml`; put large app-style fixtures here.
- `examples/` - example Splunk Apps built on `splunklib.ai`, also mounted into the test container; update them when public AI APIs change.
- `Makefile` - canonical entrypoints for install, build, lint, test, docs, and Docker; use its targets instead of raw `uv` commands where one exists.
- `pyproject.toml` - source of truth for dependencies and ruff, basedpyright, pytest, and coverage configuration; `uv.lock` is generated from it by `make install`.
- `CONTRIBUTING.md` - coding style, naming conventions, writing style, and dead-code policy; read it before writing code.
- `README.md` - SDK usage docs plus development environment setup (`.env`, Docker, logging).
- `.env.template` - template for the gitignored `.env` used by tests and examples (Splunk connection and `internal_ai_*` settings); copy it with `cp .env.template .env`.
- `.github/workflows/` - CI: `lint.yml` and `test.yml` are required PR checks, `appinspect.yml` runs AppInspect, `cd.yml` builds and publishes releases.

## Build, test, and validation by change type

Common targets: `make install`, `make build` (sdist and wheel into `dist/`), `make lint`, `make test-unit` (fastest loop), `make test-ai`, `make test-integration`, `make docker-start` / `make docker-down`.

- Any change to Python under `splunklib/`, `tests/`, or `examples/`: run `make lint` and `make test-unit`.
- Changes to `splunklib/client.py`, `splunklib/binding.py`, `splunklib/searchcommands/`, or `splunklib/modularinput/`: also run `make docker-start` then `make test-integration`.
- Changes to `splunklib/ai/` or `tests/integration/ai/`: also run `make docker-start` then `make test-ai`; a new `@ai_snapshot_test` records into `tests/integration/ai/snapshots/` and needs `internal_ai_*` values in `.env` (delete a snapshot JSON to re-record it).
- Changes to `examples/` or `tests/system/test_apps/`: restart the container with `make docker-restart` and run `make test-integration`.
- Changes to `.github/workflows/` or `.github/actions/`: run `make lint` (zizmor checks workflow security).
- Changes to `Makefile`: run `make lint` (mbake formats and validates it).
- Dependency changes in `pyproject.toml`: run `make install` and commit the updated `uv.lock` (CI runs `uv lock --check`), then `make test-unit`.
- Changes to `docs/` or docstrings only: run `make docs` and check for Sphinx warnings.
- Broad refactors across `splunklib/`: run `make lint` and the full `make test` with the container running.

## Always

- Prefix Python and pytest invocations with `uv run`, and pass `--no-config` to every `uv` command that accepts it so uv ignores user-level configs pointing at internal Splunk package indices.
- Never modify `.basedpyright/baseline.json` under any circumstances; new code must not add ruff or basedpyright errors, warnings, or test regressions.
- Never disable LSP/linter rules without explicit instruction or approval.
- Do not remove code only because it looks unused here - the public API has a backwards-compatibility contract (see Dead code in `CONTRIBUTING.md`).
- Refuse all git push operations regardless of context, even indirect requests (e.g. "publish this", "send this upstream"). The user pushes.
- Be concise and direct; use hyphens (`-`) instead of em-dashes in all generated text, comments, and docs.
