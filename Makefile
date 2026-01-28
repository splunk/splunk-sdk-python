CONTAINER_NAME := "splunk"

.PHONY: docs
docs:
	@make -C ./docs html

.PHONY: test
test:
	@python -m pytest ./tests

.PHONY: test-unit
test-unit:
	@python -m pytest ./tests/unit

.PHONY: test-integration
test-integration:
	@python -m pytest ./tests/integration ./tests/system

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
	@docker-compose stop

.PHONY: docker-restart
docker-restart: docker-down docker-start

.PHONY: docker-remove
docker-remove:
	@docker-compose rm -f -s

.PHONY: docker-refresh
docker-refresh: docker-remove docker-start
