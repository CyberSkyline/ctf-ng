# /backend/ng/plugin/Makefile

# Allow environment override
PYTHON_EXEC ?= python

ifeq ($(shell test -f ../../venv/bin/python && echo exists), exists)
    PYTHON_EXEC = ../../venv/bin/python
endif

GREEN := \033[0;32m

# Quick Lint Commands
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


# Test Commands
default: test-all

# All tests except middleware (need isolation)
test-all:
	$(PYTHON_EXEC) -m pytest -m "not middleware" -s

# Type
test-unit:
	$(PYTHON_EXEC) -m pytest admin/tests/test_admin_logic.py event/tests/test_event_models.py team/tests/test_team_models.py user/tests/test_user_models.py support/tests/test_support_models.py core/testing/system/ -v

test-integration:
	$(PYTHON_EXEC) -m pytest admin/tests/test_admin_controllers.py event/tests/test_event_controllers.py event/tests/test_event_lifecycle.py team/tests/test_captain_edge_cases.py team/tests/test_complex_team_operations.py team/tests/test_team_controllers.py user/tests/test_user_controllers.py support/tests/test_support_controllers.py -v
	
test-api:
	$(PYTHON_EXEC) -m pytest admin/tests/test_admin_api.py event/tests/test_event_api.py team/tests/test_team_api.py user/tests/test_user_api.py support/tests/test_support_api.py -v

# Domain  
test-team:
	$(PYTHON_EXEC) -m pytest team/tests/ -v

test-event:
	$(PYTHON_EXEC) -m pytest event/tests/ -v

test-event-registration:
	$(PYTHON_EXEC) -m pytest event_registration/tests/ -v

test-admin:
	$(PYTHON_EXEC) -m pytest admin/tests/ -v

test-user:
	$(PYTHON_EXEC) -m pytest user/tests/ -v

test-support:
	$(PYTHON_EXEC) -m pytest support/tests/ -v

test-utils:
	$(PYTHON_EXEC) -m pytest core/testing/system/ -v

test-middleware:
	$(PYTHON_EXEC) -m pytest -m middleware -v

# Fast feedback
test-fast:
	$(PYTHON_EXEC) -m pytest admin/tests/test_admin_logic.py event/tests/test_event_models.py team/tests/test_team_models.py user/tests/test_user_models.py support/tests/test_support_models.py -x  

.PHONY: default check fix format test-all test-unit test-integration test-api test-team test-event test-admin test-user test-support test-utils test-fast
