# Makefile

PYTHON_EXEC ?= python

VENV_PYTHON = ../venv/bin/python

ifeq ($(shell test -f $(VENV_PYTHON) && echo exists), exists)
    PYTHON_EXEC = $(VENV_PYTHON)
endif


find-TODO:
	pylint --disable=all --enable=W0511 .

# All tests
test-all:
	$(PYTHON_EXEC) -m pytest -m "not middleware" --ignore-glob="**/*e2e*" -v

test-validation:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_validation.py")

test-models:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_model.py")

test-controllers:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_controllers.py")

test-routes:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_routes.py")

test-api:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_api.py")


# Domain
test-team:
	$(PYTHON_EXEC) -m pytest ./team/tests/ -v

test-event:
	$(PYTHON_EXEC) -m pytest ./event/tests/ -v

test-admin:
	$(PYTHON_EXEC) -m pytest ./admin/tests/ -v

test-user:
	$(PYTHON_EXEC) -m pytest ./user/tests/ -v

test-support:
	$(PYTHON_EXEC) -m pytest ./support/tests/ -v

test-scoring:
	$(PYTHON_EXEC) -m pytest -s ./scoring/tests/ -v

test-challenge:
	$(PYTHON_EXEC) -m pytest -s challenge/tests/ -v

test-permissions:
	$(PYTHON_EXEC) -m pytest permissions/tests/ -v
	
test-notifications:
	$(PYTHON_EXEC) -m pytest notifications -v
	
test-middleware:
	$(PYTHON_EXEC) -m pytest -m middleware . -v

test-utils:
	$(PYTHON_EXEC) -m pytest ./core/tests/system/ -v


.PHONY: check fix format test-all test-routes test-models test-validation test-controllers test-api test-team test-event test-admin test-user test-support test-utils test-fast test-middleware test-event-registration test-scoring find-TODO
