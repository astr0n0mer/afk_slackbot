.venv:
	python -m venv .venv

.PHONY: requirements.txt
requirements.txt: .venv
	. .venv/bin/activate && \
	pip-compile --output-file requirements.txt requirements.in

.PHONY: requirements-dev.txt
requirements-dev.txt: .venv
	. .venv/bin/activate && \
	pip-compile --output-file requirements-dev.txt requirements.in requirements-dev.in

.PHONY: requirements
requirements: requirements.txt requirements-dev.txt

.PHONY: install
install: .venv
	. .venv/bin/activate && \
	pip install -r requirements.txt

.PHONY: install_dev
install_dev: install
	. .venv/bin/activate && \
	pip install -r requirements-dev.txt

.PHONY: run
run:
	. .venv/bin/activate && \
	python main.py

.PHONY: test
test:
	docker-compose --file ./docker-compose-test.yaml up --abort-on-container-exit --remove-orphans

.PHONY: cleanup
cleanup:
	docker-compose --file ./docker-compose-test.yaml down --remove-orphans
