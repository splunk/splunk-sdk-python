#
# Conveniences for splunk-sdk development
#

CONTAINER_NAME := "splunk"

# VIRTUALENV MANAGEMENT

# https://docs.astral.sh/uv/reference/cli/#uv-run--upgrade
# --no-config is used to skip all the internal Splunk package indexes
.PHONY: uv-sync
uv-sync:
	@echo "[splunk-sdk] Make sure to tun this only in the repo root!"
	uv sync --all-groups --all-extras --no-config

.PHONY: uv-upgrade
uv-upgrade:
	@echo "[splunk-sdk] Make sure to run this only in the repo root!"
	uv sync --all-groups --all-extras --upgrade --no-config

.PHONY: clean
clean: 
	rm -rf ./build ./dist ./.venv ./.ruff_cache ./.pytest_cache ./splunk_sdk.egg-info ./__pycache__ ./**/__pycache__

.PHONY: docs
docs:
	make -C ./docs html

.PHONY: test
test:
	# Previously failing tests go first
	python -m pytest --ff ./tests

.PHONY: test-unit
test-unit:
	# Previously failing tests go first
	python -m pytest --ff ./tests/unit

.PHONY: test-integration
test-integration:
	# Previously failing tests go first
	python -m pytest --ff ./tests/integration ./tests/system

.PHONY: test-ai
test-ai:
	# Previously failing tests go first
	python -m pytest --ff ./tests/integration/ai ./tests/unit/ai

.PHONY: docker-up
docker-up:
	# For podman (at least on macOS) you might need to add DOCKER_BUILDKIT=0
	# --build forces Docker to build a new image instead of using an existing one
	@docker-compose up -d --build

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
	docker-compose stop

.PHONY: docker-restart
docker-restart: docker-down docker-start

.PHONY: docker-remove
docker-remove:
	docker-compose rm -f -s

.PHONY: docker-refresh
docker-refresh: docker-remove docker-start

.PHONY: docker-splunk-restart
docker-splunk-restart:
	docker exec -it splunk sudo sh -c '/opt/splunk/bin/splunk restart --run-as-root'

.PHONY: docker-tail-python-log
docker-tail-python-log:
	docker exec splunk sudo tail /opt/splunk/var/log/splunk/python.log