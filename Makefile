# Define variables
SRC := ./manifest
TESTS := ./tests

# Define targets
.PHONY: lint test

lint:
	flake8 $(SRC)

test:
	coverage run -m pytest --junitxml=report.xml
	coverage report
	coverage xml
	coverage html -d coverage-report
