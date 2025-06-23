# Plugin Testing Architecture & Commands

## 1. Test Architecture

Our test suite is organized by **domain** and **type**. This means that tests for the "team" functionality live within the `team/tests/` directory.

### Key Components:

-   **`plugin/conftest.py`**: This is the **master configuration** for the entire test suite. It is located at the root of the plugin to ensure that its fixtures (like the database session `db_session` and the application client `client`) are globally available to all tests in all subdirectories. This is the standard `pytest` pattern for project wide shared fixtures.

-   **`plugin/core/testing/helpers.py`**: This file contains custom helper functions specific to the testing needs, such as `login_as()`. It is separate from the main CTFd test helpers to keep the custom logic isolated.

-   **`plugin/core/testing/system/`**: This directory contains unit tests for core, shared utilities. It tests things like custom middleware, API response formatters, and data converters, etc.

-   **Domain-Specific Tests (`<domain>/tests/`)**: Each domain (`admin/`, `team/`, `user/`, `event/`) has its own `tests/` subdirectory. This is where the majority of tests live, broken down by type:
    -   `test_*_models.py`: **Unit tests** that check model logic without a database. They are fast and test small pieces of code.
    -   `test_*_controllers.py`: **Integration tests** that check business logic and its interaction with the database. These require a database connection.
    -   `test_*_api.py`: **API tests** that make real HTTP requests to the application endpoints to ensure they behave correctly from an external perspective.

## 2. Running Tests with `make`

All test commands should be run from the `plugin/` directory using `make`.

## Make Commands

These commands run large suites of tests.

| Command             | Description                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| `make test-all`     | Runs all unit, integration, and API tests **except** for the isolated middleware tests. This is the main CI command. |
| `make test-middleware` | Runs only the specialized middleware tests in their own isolated application environment.                     |
| `make test-fast`    | Runs only the fastest unit tests (no database access) for quick feedback during development.              |

### Test Type Commands

These commands run all tests of a specific type across all domains.

| Command                | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `make test-unit`       | Runs all unit tests (model logic, core utilities). Fast and no database needed. |
| `make test-integration`| Runs all integration tests (controllers, complex workflows). Slower, needs database. |
| `make test-api`        | Runs all API-level tests. Slower, needs database.                           |

### Domain-Specific Commands

These commands run all tests (unit, integration, and API) for a single feature domain.

| Command          | Description                                 |
| ---------------- | ------------------------------------------- |
| `make test-admin`| Runs all tests related to the Admin domain.     |
| `make test-team` | Runs all tests related to the Team domain.      |
| `make test-event`| Runs all tests related to the Event domain.     |
| `make test-user` | Runs all tests related to the User domain.      |
| `make test-utils`| Runs all unit tests for the core utilities.     |

### Github CI/CD

The test suite contains specialized middleware tests that require a unique, isolated environment. Therefore, to run all 145 tests, you must execute two commands in sequence: first make test-all (138) for the main suite, and then make test-middleware (7) for the isolated tests. Would look something like this:


```yml
name: workflow test yml
on: [ pull_request ]
jobs:
  test:
    runs-on: ubuntu-latest # or different 
    strategy:
      matrix:
        python-version: [ '3.x.x' ] 

    steps:
      - name: Checkout repository and submodules
        uses: actions/checkout@v4
        with:
          submodules: 'recursive'

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r external/CTFd/requirements.txt
          pip install -r backend/ctfd/plugin/requirements.txt
          pip install pytest

#---------------------------------------------
#             Key Difference 
#----------------------------------------------
      - name: Run Main Test Suite (middleware next)
        id: main_tests
        working-directory: backend/ctfd/plugin
        run: make test-all
     
        # Then run the middleware test suite (regardless if main tests fail)
     
      - name: Run Middleware Test Suite
        if: always()
        working-directory: backend/ctfd/plugin
        run: make test-middleware
        
```        
