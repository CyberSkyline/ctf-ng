# /backend/ctfd/plugin/Makefile

# Allow environment override
PYTHON_EXEC ?= python

ifeq ($(shell test -f ../../venv/bin/python && echo exists), exists)
    PYTHON_EXEC = ../../venv/bin/python
endif

default: test-all

# All
test-all:
	$(PYTHON_EXEC) -m pytest -s

# Type
test-unit:
	$(PYTHON_EXEC) -m pytest tests/unit/ -v

test-integration:
	$(PYTHON_EXEC) -m pytest tests/integration/ -v
	
test-api:
	$(PYTHON_EXEC) -m pytest tests/api/ -v

# Domain  
test-team:
	$(PYTHON_EXEC) -m pytest tests/unit/team/ tests/integration/team/ tests/api/test_team_api.py -v

test-event:
	$(PYTHON_EXEC) -m pytest tests/unit/event/ tests/integration/event/ tests/api/test_event_api.py -v

test-admin:
	$(PYTHON_EXEC) -m pytest tests/unit/admin/ tests/integration/admin/ tests/api/test_admin_api.py -v

test-user:
	$(PYTHON_EXEC) -m pytest tests/unit/user/ tests/integration/user/ tests/api/test_user_api.py -v

test-utils:
	$(PYTHON_EXEC) -m pytest tests/unit/utils/ -v

# Fast feedback
test-fast:
	$(PYTHON_EXEC) -m pytest tests/unit/ -x  

.PHONY: default test-all test-unit test-integration test-api test-team test-event test-admin test-user test-utils test-fast
