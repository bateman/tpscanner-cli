.SHELLARGS = -eu -c

DEFAULT_GOAL := help

.PHONY: help format lint clean precommit run update patch minor major bump_version check_poetry

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
	@echo "patch     - bump the patch version"
	@echo "minor     - bump the minor version"
	@echo "major     - bump the major version"

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

update: check_poetry
	poetry update
	poetry lock --no-update
	poetry run pre-commit autoupdate

install: check_poetry
	poetry install
	poetry lock --no-update
	poetry run pre-commit install

export: check_poetry pyproject.toml
	poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev
	poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev

build: check_poetry pyproject.toml
	poetry build

patch: check_poetry
	poetry version patch
	$(MAKE) bump_version

minor: check_poetry
	poetry version minor
	$(MAKE) bump_version

major: check_poetry
	poetry version major
	$(MAKE) bump_version

bump_version: check_poetry
	$(eval version=$(shell poetry version))
	$(eval version_number=$(shell echo $(version) | awk '{print $$NF}'))
	echo "Bump version to $(version_number)"
	git add pyproject.toml
	git commit -m "Bump version to $(version_number)"
	git tag $(version_number)
	git push origin $(version_number)

check_poetry:
	@which poetry >/dev/null || (echo "Poetry is not installed"; exit 1)