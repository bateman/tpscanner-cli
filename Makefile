.PHONY: format lint clean precommit

format:
	ruff format

lint:
	ruff check

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

precommit: format lint
	pre-commit run --all-files

run:
	python -m tpscanner $@