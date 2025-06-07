# How to test 

#### /plugin/tests/unit/
*   `test_config.py` - Sanity checks for the main config settings

#### /plugin/tests/integration/
*   `test_models.py` - Tests the database models and their relationships
*   `test_controllers.py` - Tests the core business logic in the controllers
*   `test_constraints.py` - Verifies database rules

#### /plugin/tests/api/
*   `test_admin_api.py` - Tests the admin only endpoints.
*   `test_teams_api.py` - Tests team creation and management endpoints
*   `test_users_api.py` - Tests user specific endpoints
*   `test_worlds_api.py` - Tests world creation and listing endpoints

#### /plugin/tests/fixtures/
*   `conftest.py` - Shared pytest fixtures
*   `reset_database.py` - Script to reset the db
*   `seed_data.py` - Script to fill the database with sample data


## Commands

```bash
make test-unit        # unit tests
make test-models      # model tests
make test-controllers # controller tests
make test-api         # api tests
make test-constraints # db constraints
make test-all         # all tests

# utils  
make test-with-data   # reset db + seed + test models/controllers
make reset-db         # just reset database
make seed-db          # just generate seed data
```

**no app context needed**
- config value validation
- string manipulation functions
- utility functions that don't use database
- input validation logic

**app context needed**
- model creation/queries
- database relationships
- constraint enforcement
- controller business logic
- seed data generation
