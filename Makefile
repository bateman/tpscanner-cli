.SHELLARGS = -eu -c

DEFAULT_GOAL := help

.PHONY: help format lint clean precommit run update

help:
	@echo "help      - show this help"
	@echo "format    - format code"
	@echo "lint      - lint code"
	@echo "clean     - remove temporary files"
	@echo "precommit - run pre-commit checks"
	@echo "run       - run the application"
	@echo "install   - install the project dependencies"
	@echo "update    - update the project dependencies"

format:
	ruff format

lint: format
	ruff check

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

precommit: format lint
	pre-commit run --all-files

run:
	python -m tpscanner $@

update:
	poetry update
	poetry lock --no-update
	poetry run pre-commit autoupdate

install:
	poetry install
	poetry lock --no-update
	poetry run pre-commit install
