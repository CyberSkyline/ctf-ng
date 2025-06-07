# /plugin/makefile

PYTHON_EXEC = ../../../backend/venv/bin/python

default: test-all

# Run all tests
test-all:
	$(PYTHON_EXEC) -m pytest -s


# Unit tests
test-unit:
	$(PYTHON_EXEC) -m pytest tests/unit/ -s

# Model tests
test-models:
	$(PYTHON_EXEC) -m pytest tests/integration/test_models.py -s

# Controller tests
test-controllers:
	$(PYTHON_EXEC) -m pytest tests/integration/test_controllers.py -s

# Database constraint tests
test-constraints:
	$(PYTHON_EXEC) -m pytest tests/integration/test_constraints.py -s

# API tests
test-api:
	$(PYTHON_EXEC) -m pytest tests/api/ -s


# Reset the plugin's database tables
reset-db:
	$(PYTHON_EXEC) tests/fixtures/reset_database.py

# Seed the database with test data
seed-db:
	cd ../../../../external/CTFd && flask shell -c "import sys; sys.path.append('../../backend/ctfd/plugin/tests/fixtures'); from seed_data import demo_seed; demo_seed()"

.PHONY: default test-all test-unit test-models test-controllers test-constraints test-api reset-db seed-db
