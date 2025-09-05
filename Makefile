eval:
	python -m eval.run_eval

setup:
	pip install -r requirements.txt

run:
	python -m src.main

test:
	pytest

test-verbose:
	pytest -v -s

.PHONY: eval setup run test test-verbose