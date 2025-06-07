# How to Test

This plugin uses the `pytest` framework for testing.

#### /plugin/tests/unit/
Contains fast unit tests that do not require a database or application context.
*   `test_config.py` - Sanity checks for the main config settings.
*   `test_validators.py` - Sanity checks for validation utility functions.

#### /plugin/tests/integration/
Contains tests for components that require a database connection and application context to verify their interactions.
*   `test_models.py` - Tests the database models and their relationships.
*   `test_controllers.py` - Tests the core business logic in the controllers.
*   `test_constraints.py` - Verifies low-level database rules like unique constraints.

#### /plugin/tests/api/
Contains tests that interact with the live API endpoints, simulating requests and checking responses.
*   `test_api.py` - Covers all basic API endpoints.

#### /plugin/tests/
*   `conftest.py` - Contains shared fixtures used by `pytest` to set up the test environment, create mock data, and manage the database state.

---

### Utility Scripts

The `tests/fixtures/` directory contains standalone scripts that are **not** part of the automated `pytest` suite. They are placeholders and can be used for manual database operations during development.

*   `reset_database.py`: A manual script to wipe all plugin related tables from the database (placeholder).
*   `seed_data.py`: A manual script to populate the database with a large set of sample data for demonstration or exploratory testing (placeholder).

**Note:** The automated test suite, driven by `conftest.py`, creates all the necessary data for its own execution and cleans up after itself. The scripts above are for manual use only.

---

## Running Tests

The `Makefile` in the parent directory provides convenient shortcuts for running tests.

### Main Commands
```bash
make test-all         # Runs all tests
make test-unit        # Runs only the fast, database independent unit tests
make test-integration # Runs all database-dependent tests.
make test-api         # Focuses on just the API endpoint tests.
make test-controllers # Focuses on just the controller logic tests.
make test-models      # Focuses on just the database model tests.
make test-constraints # Focuses on just the database constraint tests.
```

### Unit Tests

#### `test_config.py`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_default_team_size`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_max_team_size`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_invite_code_generation_attempts`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_min_team_size`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_invite_code_length`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_database_field_lengths`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_empty_teams_warning_threshold`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_admin_confirmation_strings`
*   `python -m pytest tests/unit/test_config.py::TestConfig::test_team_size_constraints_are_logical`

#### `test_validators.py`
*   `python -m pytest tests/unit/test_validators.py::TestValidators::test_validation_error_message_templates`

---

### Integration Tests (`/tests/integration/`)

#### `test_constraints.py`
*   `python -m pytest tests/integration/test_constraints.py::TestConstraints::test_unique_user_world_constraint`
*   `python -m pytest tests/integration/test_constraints.py::TestConstraints::test_team_member_count_property`
*   `python -m pytest tests/integration/test_constraints.py::TestConstraints::test_unique_invite_codes`

#### `test_controllers.py`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_team_creation_with_invite_codes`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_joining_full_team_fails`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_invite_code_joining`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_world_default_team_size`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_manual_captain_assignment`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_auto_captain_assignment`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_government_training_scenario`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_update_team_captain_only`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_disband_team_captain_only`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_remove_member_captain_only`
*   `python -m pytest tests/integration/test_controllers.py::TestControllers::test_creator_already_in_team`

#### `test_models.py`
*   `python -m pytest tests/integration/test_models.py::TestModels::test_create_world`
*   `python -m pytest tests/integration/test_models.py::TestModels::test_create_team`
*   `python -m pytest tests/integration/test_models.py::TestModels::test_create_user`
*   `python -m pytest tests/integration/test_models.py::TestModels::test_team_membership`

---

### API Tests (`/tests/api/`)

#### `test_api.py`
*   `python -m pytest tests/api/test_api.py::test_teams_endpoint_requires_authentication`
*   `python -m pytest tests/api/test_api.py::test_teams_endpoint_with_authentication`
*   `python -m pytest tests/api/test_api.py::test_worlds_endpoint_with_authentication`
*   `python -m pytest tests/api/test_api.py::test_users_me_teams_endpoint`
*   `python -m pytest tests/api/test_api.py::test_admin_endpoints_require_admin`
*   `python -m pytest tests/api/test_api.py::test_admin_endpoint_with_admin_user`
*   `python -m pytest tests/api/test_api.py::test_create_team_requires_data`
*   `python -m pytest tests/api/test_api.py::test_create_world_is_forbidden_for_normal_user`
*   `python -m pytest tests/api/test_api.py::test_create_world_succeeds_for_admin_user`
*   `python -m pytest tests/api/test_api.py::test_create_team_creator_becomes_captain`
*   `python -m pytest tests/api/test_api.py::test_captain_assignment_security`
*   `python -m pytest tests/api/test_api.py::test_update_team_endpoint_security`
*   `python -m pytest tests/api/test_api.py::test_join_team_fails_if_already_in_a_team_in_world`
