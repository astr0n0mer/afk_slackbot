.PHONY: dev
dev: install_dev run

.venv:
	uv venv --clear

.PHONY: install
install: .venv
	. .venv/bin/activate && \
	uv sync --no-dev

.PHONY: install_dev
install_dev:
	. .venv/bin/activate && \
	uv sync

.PHONY: upgrade_dependencies
upgrade_dependencies: .venv install_dev
	. .venv/bin/activate && \
	uv sync --upgrade

.PHONY: run
run: .venv
	. .venv/bin/activate && \
	python main.py

.PHONY: test
test:
	docker-compose --file ./docker-compose-test.yaml up --abort-on-container-exit --remove-orphans

.PHONY: cleanup
cleanup:
	docker-compose --file ./docker-compose-test.yaml down --remove-orphans

.PHONY: cleanup_deep
cleanup_deep: cleanup
	docker rmi afk_slackbot-tester

.PHONY: lint
lint:
	. .venv/bin/activate && \
	pyright .

.PHONY: format
format:
	. .venv/bin/activate && \
	ruff format .

.PHONY: group_dependabot_prs
group_dependabot_prs:
	git fetch --all & \
	git switch --create grouped_dependency_upgrade && \
	git branch --all | grep dependabot | xargs -I {} git merge {} && \
	gh pr create \
		--title "build(deps): grouped dependabot upgrades" \
		--fill-verbose \
		--assignee "@me"
