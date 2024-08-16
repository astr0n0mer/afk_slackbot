.venv:
	python -m venv .venv

.PHONY: requirements.txt
requirements.txt: .venv
	source .venv/bin/activate && \
	pip-compile --output-file requirements.txt requirements.in

.PHONY: requirements-dev.txt
requirements-dev.txt: .venv
	source .venv/bin/activate && \
	pip-compile --output-file requirements-dev.txt requirements-dev.in

requirements: requirements.txt requirements-dev.txt

.PHONY: install
install: .venv
	source .venv/bin/activate && \
	pip install -r requirements.txt

.PHONY: install_dev
install_dev: install
	source .venv/bin/activate && \
	pip install -r requirements-dev.txt
