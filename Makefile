.SHELLARGS = -eu -c

DEFAULT_GOAL := help

.PHONY: help format lint clean precommit run update

help:
	@echo "help      - show this help"
	@echo "run       - run the application"
	@echo "format    - format code"
	@echo "lint      - lint code"
	@echo "precommit - run pre-commit checks"
	@echo "clean     - remove temporary files"
	@echo "install   - install the project dependencies"
	@echo "update    - update the project dependencies"
	@echo "export    - export the project dependencies"
	@echo "build     - build the project release"

format:
	ruff format

lint: format
	ruff check

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf dist

precommit: format lint
	pre-commit run --all-files

ARGS = ""
run:
	python -m tpscanner $(ARGS)

update:
	poetry update
	poetry lock --no-update
	poetry run pre-commit autoupdate

install:
	poetry install
	poetry lock --no-update
	poetry run pre-commit install

export: pyproject.toml
	poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev
	poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev

build: pyproject.toml
	poetry build