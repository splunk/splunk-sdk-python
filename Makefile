# text reset
NO_COLOR=\033[0m
# green
OK_COLOR=\033[32;01m
# red
ERROR_COLOR=\033[31;01m
# cyan
WARN_COLOR=\033[36;01m
# yellow
ATTN_COLOR=\033[33;01m

ROOT_DIR := $(shell git rev-parse --show-toplevel)

VERSION := `git describe --tags --dirty 2>/dev/null`
COMMITHASH := `git rev-parse --short HEAD 2>/dev/null`
DATE := `date "+%FT%T%z"`

CONTAINER_NAME := 'splunk'

.PHONY: all
all: test

init:
	@echo "$(ATTN_COLOR)==> init $(NO_COLOR)"

.PHONY: docs
docs:
	@echo "$(ATTN_COLOR)==> docs $(NO_COLOR)"
	@rm -rf ./docs/_build
	@tox -e docs
	@cd ./docs/_build/html && zip -r ../docs_html.zip . -x ".*" -x "__MACOSX"
	@echo "$(ATTN_COLOR)==> Docs pages can be found at ./docs/_build/html, docs bundle available at ./docs/_build/docs_html.zip"

.PHONY: test
test:
	@echo "$(ATTN_COLOR)==> test $(NO_COLOR)"
	@tox -e py37,py39

.PHONY: test_specific
test_specific:
	@echo "$(ATTN_COLOR)==> test_specific $(NO_COLOR)"
	@sh ./scripts/test_specific.sh

.PHONY: test_smoke
test_smoke:
	@echo "$(ATTN_COLOR)==> test_smoke $(NO_COLOR)"
	@tox -e py27,py37 -- -m smoke

.PHONY: test_no_app
test_no_app:
	@echo "$(ATTN_COLOR)==> test_no_app $(NO_COLOR)"
	@tox -e py27,py37 -- -m "not app"

.PHONY: test_smoke_no_app
test_smoke_no_app:
	@echo "$(ATTN_COLOR)==> test_smoke_no_app $(NO_COLOR)"
	@tox -e py27,py37 -- -m "smoke and not app"

.PHONY: env
env:
	@echo "$(ATTN_COLOR)==> env $(NO_COLOR)"
	@echo "To make a .env:"
	@echo "  [SPLUNK_INSTANCE_JSON] | python scripts/build-env.py"

.PHONY: env_default
env_default:
	@echo "$(ATTN_COLOR)==> env_default $(NO_COLOR)"
	@python scripts/build-env.py

.PHONY: up
up:
	@echo "$(ATTN_COLOR)==> up $(NO_COLOR)"
	@docker-compose up -d

.PHONY: remove
remove:
	@echo "$(ATTN_COLOR)==> rm $(NO_COLOR)"
	@docker-compose rm -f -s

.PHONY: wait_up
wait_up:
	@echo "$(ATTN_COLOR)==> wait_up $(NO_COLOR)"
	@for i in `seq 0 180`; do if docker exec -it $(CONTAINER_NAME) /sbin/checkstate.sh &> /dev/null; then break; fi; printf "\rWaiting for Splunk for %s seconds..." $$i; sleep 1; done

.PHONY: down
down:
	@echo "$(ATTN_COLOR)==> down $(NO_COLOR)"
	@docker-compose stop

.PHONY: start
start: up wait_up

.PHONY: restart
restart: down start

.PHONY: refresh
refresh: remove start
