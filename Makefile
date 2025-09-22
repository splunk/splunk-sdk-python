RESET_COLOR=\033[0m
GREEN_COLOR=\033[32;01m

CONTAINER_NAME := 'splunk'

.PHONY: docs
docs:
	@echo "$(GREEN_COLOR)==> docs $(RESET_COLOR)"
	@rm -rf ./docs/_build
	@make -C ./docs html
	@echo "$(GREEN_COLOR)==> Docs pages can be found at docs/_build/html"
	@echo "$(GREEN_COLOR)==> Docs bundle available at docs/_build/docs_html.zip"

.PHONY: test
test:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests

.PHONY: test-unit
test-unit:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests/unit

.PHONY: test-integration
test-integration:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests/integration ./tests/system

.PHONY: docker-up
docker-up:
	@echo "$(GREEN_COLOR)==> up $(RESET_COLOR)"
	@docker-compose up -d

.PHONY: docker-remove
docker-remove:
	@echo "$(GREEN_COLOR)==> rm $(RESET_COLOR)"
	@docker-compose rm -f -s

.PHONY: docker-ensure-up
docker-ensure-up:
	@echo "$(GREEN_COLOR)==> wait-up $(RESET_COLOR)"
	@for i in `seq 0 180`; do if docker exec -it $(CONTAINER_NAME) /sbin/checkstate.sh &> /dev/null; then break; fi; printf "\rWaiting for Splunk for %s seconds..." $$i; sleep 1; done

.PHONY: docker-down
docker-down:
	@echo "$(GREEN_COLOR)==> down $(RESET_COLOR)"
	@docker-compose stop

.PHONY: docker-start
docker-start: docker-up docker-ensure-up

.PHONY: docker-restart
docker-restart: docker-down docker-start

.PHONY: docker-refresh
docker-refresh: docker-remove docker-start
