RESET_COLOR=\033[0m
GREEN_COLOR=\033[32;01m

CONTAINER_NAME := 'splunk'

.PHONY: docs
docs:
	@echo "$(GREEN_COLOR)==> docs $(RESET_COLOR)"
	@rm -rf ./docs/_build
	@tox -e docs
	@cd ./docs/_build/html && zip -r ../docs_html.zip . -x ".*" -x "__MACOSX"
	@echo "$(ATTN_COLOR)==> Docs pages can be found at ./docs/_build/html, docs bundle available at ./docs/_build/docs_html.zip"

.PHONY: test
test:
	@echo "$(GREEN_COLOR)==> test $(RESET_COLOR)"
	@tox -e py

.PHONY: up
up:
	@echo "$(GREEN_COLOR)==> up $(RESET_COLOR)"
	@docker-compose up -d

.PHONY: remove
remove:
	@echo "$(GREEN_COLOR)==> rm $(RESET_COLOR)"
	@docker-compose rm -f -s

.PHONY: wait_up
wait_up:
	@echo "$(GREEN_COLOR)==> wait_up $(RESET_COLOR)"
	@for i in `seq 0 180`; do if docker exec -it $(CONTAINER_NAME) /sbin/checkstate.sh &> /dev/null; then break; fi; printf "\rWaiting for Splunk for %s seconds..." $$i; sleep 1; done

.PHONY: down
down:
	@echo "$(GREEN_COLOR)==> down $(RESET_COLOR)"
	@docker-compose stop

.PHONY: start
start: up wait_up

.PHONY: restart
restart: down start

.PHONY: refresh
refresh: remove start
