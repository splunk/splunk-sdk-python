RESET_COLOR=\033[0m
GREEN_COLOR=\033[32;01m

CONTAINER_NAME := 'splunk'

.PHONY: docs test test-unit test-integration up wait_up remove down refresh start restart finish
docs:
	@echo "$(GREEN_COLOR)==> docs $(RESET_COLOR)"
	@rm -rf ./docs/_build
	@make -C ./docs html
	@echo "$(GREEN_COLOR)==> Docs pages can be found at docs/_build/html"
	@echo "$(GREEN_COLOR)==> Docs bundle available at docs/_build/docs_html.zip"

test:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests

test:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests/unit

test:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@python -m pytest ./tests/integration ./tests/system

up:
	@echo "$(GREEN_COLOR)==> up $(RESET_COLOR)"
	@docker-compose up -d

remove:
	@echo "$(GREEN_COLOR)==> rm $(RESET_COLOR)"
	@docker-compose rm -f -s

wait_up:
	@echo "$(GREEN_COLOR)==> wait_up $(RESET_COLOR)"
	@for i in `seq 0 180`; do if docker exec -it $(CONTAINER_NAME) /sbin/checkstate.sh &> /dev/null; then break; fi; printf "\rWaiting for Splunk for %s seconds..." $$i; sleep 1; done

down:
	@echo "$(GREEN_COLOR)==> down $(RESET_COLOR)"
	@docker-compose stop

start: up wait_up

restart: down start

refresh: remove start
