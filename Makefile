.PHONY: test lint

test:
	pytest

lint:
	pre-commit run --all-files
