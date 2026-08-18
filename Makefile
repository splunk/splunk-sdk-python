### Conveniences for splunk-sdk-python development

## VIRTUALENV MANAGEMENT

# https://docs.astral.sh/uv/reference/cli/#uv-sync
# --no-config skips Splunk's internal PyPI mirror
UV_SYNC_CMD := uv sync --no-config
# https://docs.astral.sh/uv/reference/cli/#uv-run
UV_RUN_CMD := uv run
# https://docs.zizmor.sh/usage
ZIZMOR_CMD := $(UV_RUN_CMD) zizmor --pedantic --strict-collection

.PHONY: install
install:
	$(UV_SYNC_CMD) --dev

.PHONY: upgrade
upgrade:
	$(UV_SYNC_CMD) --dev --upgrade

# Workaround for make being unable to pass arguments to underlying cmd
# $ SDK_DEPS_GROUP="build" make ci-install
.PHONY: ci-install
ci-install:
	$(UV_SYNC_CMD) --frozen --group $(SDK_DEPS_GROUP)

.PHONY: lint
lint: lint-python lint-gh-actions lint-makefile

.PHONY: lint-gh-actions
lint-gh-actions:
	$(ZIZMOR_CMD) ./.github

.PHONY: lint-python
lint-python:
	$(UV_RUN_CMD) ruff check --fix-only
	$(UV_RUN_CMD) ruff format
	$(UV_RUN_CMD) basedpyright

.PHONY: lint-makefile
lint-makefile:
	$(UV_RUN_CMD) mbake format --config ./.bake.toml Makefile docs/Makefile

.PHONY: ci-lint
ci-lint: ci-lint-python ci-lint-gh-actions ci-lint-makefile

.PHONY: ci-lint-gh-actions
ci-lint-gh-actions:
	$(ZIZMOR_CMD) ./.github

.PHONY: ci-lint-python
ci-lint-python:
	$(UV_RUN_CMD) ruff check --fix-only --exit-non-zero-on-fix
	$(UV_RUN_CMD) ruff format --check
	$(UV_RUN_CMD) basedpyright

.PHONY: ci-lint-makefile
ci-lint-makefile:
	$(UV_RUN_CMD) mbake format --config ./.bake.toml --check Makefile docs/Makefile
	$(UV_RUN_CMD) mbake validate --config ./.bake.toml Makefile docs/Makefile

.PHONY: ci-lint-makefile
ci-lint-makefile:
	$(UV_RUN_CMD) mbake format --config ./.bake.toml --check Makefile docs/Makefile
	$(UV_RUN_CMD) mbake validate --config ./.bake.toml Makefile docs/Makefile

.PHONY: clean
clean:
	rm -rf ./build ./dist ./.venv ./.ruff_cache ./.pytest_cache ./splunk_sdk.egg-info ./__pycache__ ./**/__pycache__

.PHONY: docs
docs:
	make -C ./docs html

## TESTING

# --ff lets previously failing tests go first
# -ra prints a report on all failed tests after a run
# -vv shows why a test failed while the rest of the suite is running
PYTHON_CMD := uv run python
PYTEST_CMD := $(PYTHON_CMD) -m pytest --no-header --ff -ra -vv

.PHONY: test
test:
	$(PYTEST_CMD) ./tests

.PHONY: test-unit
test-unit:
	$(PYTEST_CMD) ./tests/unit

.PHONY: test-integration
test-integration:
	$(PYTEST_CMD) --ff ./tests/integration ./tests/system

.PHONY: test-ai
test-ai:
	$(PYTEST_CMD) ./tests/integration/ai ./tests/unit/ai

## DOCKER

CONTAINER_NAME := splunk
SPLUNK_HOME := /opt/splunk

.PHONY: docker-up
docker-up:
	# For podman (at least on macOS) you might need to add DOCKER_BUILDKIT=0
	# --build forces Docker to build a new image instead of using an existing one
	docker compose up -d --build

.PHONY: docker-ensure-up
docker-ensure-up:
	@for i in `seq 0 180`; do \
		if docker exec -it $(CONTAINER_NAME) /bin/bash -c "/sbin/checkstate.sh &> /dev/null"; then \
			break; \
		fi; \
		printf "\rWaiting for Splunk for %s seconds..." $$i; \
		sleep 1; \
	done

.PHONY: docker-start
docker-start: docker-up docker-ensure-up

.PHONY: docker-down
docker-down:
	docker compose stop

.PHONY: docker-restart
docker-restart: docker-down docker-start

.PHONY: docker-remove
docker-remove:
	docker compose rm -f -s

.PHONY: docker-refresh
docker-refresh: docker-remove docker-start

.PHONY: docker-splunk-restart
docker-splunk-restart:
	docker exec -it $(CONTAINER_NAME) sudo sh -c '$(SPLUNK_HOME)/bin/splunk restart --run-as-root'

.PHONY: docker-tail-python-log
docker-tail-python-log:
	docker exec -it $(CONTAINER_NAME) sudo tail $(SPLUNK_HOME)/var/log/splunk/python.log
