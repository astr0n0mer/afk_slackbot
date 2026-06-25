UV ?= uv
COMPOSE ?= docker compose
TEST_PYTHON ?= 3.14

.PHONY: dev
dev: install_dev run

.PHONY: install
install:
	$(UV) sync --no-dev

.PHONY: install_dev
install_dev:
	$(UV) sync

.PHONY: upgrade_dependencies
upgrade_dependencies:
	$(UV) sync --upgrade

.PHONY: run
run:
	$(UV) run python main.py

.PHONY: test
test:
	TEST_PYTHON=$(TEST_PYTHON) $(COMPOSE) --file ./docker-compose-test.yaml up --build --abort-on-container-exit --remove-orphans

.PHONY: test_local
test_local:
	$(UV) run --python $(TEST_PYTHON) pytest

.PHONY: cleanup
cleanup:
	$(COMPOSE) --file ./docker-compose-test.yaml down --remove-orphans

.PHONY: cleanup_deep
cleanup_deep: cleanup
	docker rmi afk_slackbot-tester

.PHONY: lint
lint:
	$(UV) run pyright .

.PHONY: format
format:
	$(UV) run ruff format .

.PHONY: group_dependabot_prs
group_dependabot_prs:
	git fetch --all & \
	git switch --create grouped_dependency_upgrade && \
	git branch --all | grep dependabot | xargs -I {} git merge {} && \
	gh pr create \
		--title "build(deps): grouped dependabot upgrades" \
		--fill-verbose \
		--assignee "@me"
