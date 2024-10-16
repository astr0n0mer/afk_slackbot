.PHONY: dev
dev: install_dev run

.venv:
	python -m venv .venv

requirements.txt: .venv requirements.in
	. .venv/bin/activate && \
	pip-compile --output-file requirements.txt requirements.in

requirements-dev.txt: .venv requirements.in requirements-dev.in
	. .venv/bin/activate && \
	pip-compile --output-file requirements-dev.txt requirements-dev.in

.PHONY: requirements
requirements: requirements.txt requirements-dev.txt

.PHONY: install
install: .venv
	. .venv/bin/activate && \
	pip install -r requirements.txt

.PHONY: install_dev
install_dev: .venv
	. .venv/bin/activate && \
	pip install -r requirements-dev.txt

.PHONY: upgrade_dependencies
upgrade_dependencies:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

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
