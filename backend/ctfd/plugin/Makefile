# /backend/ctfd/plugin/Makefile

# Allow environment override
PYTHON_EXEC ?= python

ifeq ($(shell test -f ../../venv/bin/python && echo exists), exists)
	PYTHON_EXEC = ../../venv/bin/python
endif

default: test-all

# Install dependencies
install-deps:
	$(PYTHON_EXEC) -m pip install --upgrade pip
	$(PYTHON_EXEC) -m pip install -r requirements.txt
	$(PYTHON_EXEC) -m pip install -r $(CURDIR)/../../external/CTFd/requirements.txt

# All
test-all: install-deps
	$(PYTHON_EXEC) -m pytest -s

# Type
test-unit: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/ -v

test-integration: install-deps
	$(PYTHON_EXEC) -m pytest tests/integration/ -v
	
test-api: install-deps
	$(PYTHON_EXEC) -m pytest tests/api/ -v

# Domain  
test-team: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/team/ tests/integration/team/ tests/api/test_team_api.py -v

test-event: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/event/ tests/integration/event/ tests/api/test_event_api.py -v

test-admin: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/admin/ tests/integration/admin/ tests/api/test_admin_api.py -v

test-user: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/user/ tests/integration/user/ tests/api/test_user_api.py -v

test-utils: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/utils/ -v

# Fast feedback
test-fast: install-deps
	$(PYTHON_EXEC) -m pytest tests/unit/ -x  

.PHONY: default install-deps test-all test-unit test-integration test-api test-team test-event test-admin test-user test-utils test-fast
