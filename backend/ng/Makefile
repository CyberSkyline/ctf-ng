# Makefile

PYTHON_EXEC ?= python

VENV_PYTHON = ../venv/bin/python

ifeq ($(shell test -f $(VENV_PYTHON) && echo exists), exists)
    PYTHON_EXEC = $(VENV_PYTHON)
endif

GREEN := \033[0;32m


check:
	@echo "$(GREEN)Running Ruff linter...$(NC)"
	@$(PYTHON_EXEC) -m ruff check .

fix:
	@echo "$(GREEN)Running Ruff linter with auto-fix...$(NC)"
	@$(PYTHON_EXEC) -m ruff check . --fix
	@echo "$(GREEN)✅ Fixes applied.$(NC)"

format:
	@echo "$(GREEN)Running Ruff formatter...$(NC)"
	@$(PYTHON_EXEC) -m ruff format .
	@echo "$(GREEN)✅ Formatting complete.$(NC)"



# All tests
test-all:
	$(PYTHON_EXEC) -m pytest .


# Test types
test-logic:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_logic.py")

test-models:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_models.py")

test-validation:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_validation.py")

test-controllers:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_controllers.py")

test-integration:
	$(PYTHON_EXEC) -m pytest -v $(shell find . -name "test_*_integration.py")


# Domain
test-team:
	$(PYTHON_EXEC) -m pytest ./team/tests/ -v

test-event:
	$(PYTHON_EXEC) -m pytest ./event/tests/ -v

test-event-registration:
	$(PYTHON_EXEC) -m pytest event_registration/tests/ -v

test-admin:
	$(PYTHON_EXEC) -m pytest ./admin/tests/ -v

test-user:
	$(PYTHON_EXEC) -m pytest ./user/tests/ -v

test-support:
	$(PYTHON_EXEC) -m pytest ./support/tests/ -v

test-utils:
	$(PYTHON_EXEC) -m pytest ./core/testing/system/ -v

test-middleware:
	$(PYTHON_EXEC) -m pytest -m middleware . -v


.PHONY: check fix format test-all test-logic test-models test-validation test-controllers test-integration test-team test-event test-admin test-user test-support test-utils test-fast test-middleware dev check-install start prod-start stop reload restart restart-nginx logs-ctfd logs-vite logs-nginx nuke-frontend
