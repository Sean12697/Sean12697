.PHONY: install dev test lint format check preview render env-example clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

check:
	profile-gen check

preview:
	profile-gen render --offline --stdout

render:
	profile-gen render

env-example:
	profile-gen settings --env-example > .env.example

clean:
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
