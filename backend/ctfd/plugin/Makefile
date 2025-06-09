# /plugin/makefile

# Allow environment override, default to python in PATH
PYTHON_EXEC ?= python

# For local development, prefer the venv if it exists
ifeq ($(shell test -f ../../../backend/venv/bin/python && echo exists), exists)
    PYTHON_EXEC = ../../../backend/venv/bin/python
endif

default: test-all

# Run all tests
test-all:
	$(PYTHON_EXEC) -m pytest -s

# Unit tests
test-unit:
	$(PYTHON_EXEC) -m pytest -m "not db" -s

# Integration and API tests
test-integration:
	$(PYTHON_EXEC) -m pytest -m "db" -s

# Models Test
test-models:
	$(PYTHON_EXEC) -m pytest tests/integration/test_models.py -s

# Controllers Tests
test-controllers:
	$(PYTHON_EXEC) -m pytest tests/integration/test_controllers.py -s

# Constraints Test
test-constraints:
	$(PYTHON_EXEC) -m pytest tests/integration/test_constraints.py -s

# Endpoint Tests
test-api:
	$(PYTHON_EXEC) -m pytest tests/api/ -s


.PHONY: default test-all test-unit test-integration test-models test-controllers test-constraints test-api
