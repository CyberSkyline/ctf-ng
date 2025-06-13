# How to Test

### **Test Types**
- **`unit/`** - Fast tests (<1s each)
- **`integration/`** - Medium tests (1-5s each)
- **`api/`** - Slower tests (2-10s each)

---

## Running Tests

### **By Test Type (Speed)**
```bash
make test-unit           # Fast tests only
make test-integration    # Database tests only
make test-api           # API endpoint tests only
make test-all           # Everything
```

### **By Domain**
```bash
make test-team          # All team-related tests (unit + integration + api)
make test-event         # All event related tests
make test-admin         # All admin related tests  
make test-user          # All user related tests
make test-utils         # Utility function tests
```

### **Development Workflow**
```bash
make test-fast          # Unit tests only, stop on first failure
```

---

## Test Coverage by Domain

### **Team Domain** 
- **Models**: Team creation, invite code generation, membership relationships, constraints
- **Controllers**: Create, join, leave, captain management, locking rules, invite code regeneration
- **API**: Authentication, permissions, team lifecycle endpoints
- **Edge Cases**: Captain removal scenarios, headless team recovery, succession chains
- **Integration**: Full team lifecycle, concurrent operations, member limit enforcement

### **Event Domain** 
- **Models**: Event creation, time constraints, locking mechanism
- **Controllers**: Event creation/update with validation, listing with statistics
- **API**: Admin only event creation, event listing, event management
- **Integration**: Event lifecycle, team isolation, time constraint validation

### **User Domain**
- **Models**: User creation, plugin user extensions, team membership tracking
- **Controllers**: Cross-event team membership, user statistics, team eligibility
- **API**: User team information endpoints

### **Admin Domain**
- **Controllers**: System statistics, data cleanup, headless team recovery, orphaned data detection
- **API**: Admin only endpoints, system health checks
- **Logic**: Data processing algorithms, cleanup algorithms, validation workflows

### **Utils Domain**
- **Validators**: Input validation, business rule enforcement, domain specific validation
- **Data Conversion**: Database row transformation, field mapping, type handling
- **API Responses**: Response formatting, error handling, success messages
- **Config**: Configuration validation and constraints

---

## Adding New Tests

### **Unit Tests**
```bash
# Create in: tests/unit/{domain}/test_{feature}.py
tests/unit/team/test_team_validation.py
tests/unit/event/test_event_rules.py
```

### **Integration Tests**  
```bash
# Create in: tests/integration/{domain}/test_{feature}.py
tests/integration/team/test_team_business_logic.py
tests/integration/event/test_event_lifecycle.py
```

### **API Tests**
```bash
# Add to existing: tests/api/test_{domain}_api.py
tests/api/test_team_api.py      # Team endpoints
tests/api/test_event_api.py     # Event endpoints
```

---

## Test Database Management

Tests use isolated database transactions via `conftest.py`:
- ✅ **Automatic cleanup** - Each test gets fresh database state
- ✅ **Fast execution** - Transactions rollback instead of full table clearing
- ✅ **Parallel safe** - Tests can run concurrently
- ✅ **Fixture-based** - Reusable test data setup

---


## Manual Testing Scripts (placeholders)

The `tests/fixtures/` directory contains development utilities:
- `reset_database.py` - Manual database cleanup (placeholder)
- `seed_data.py` - Sample data generation (placeholder)

---

### **Unit Tests (`tests/unit/`)**

#### `plugin/tests/unit/admin/test_admin_logic.py`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_data_counts_calculation_logic`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_empty_teams_threshold_calculation`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_health_check_warning_generation`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_orphaned_data_identification_logic`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_headless_team_detection_algorithm`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_oldest_member_promotion_logic`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_orphaned_user_identification`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_admin_reset_confirmation_required`
*   `python -m pytest plugin/tests/unit/admin/test_admin_logic.py::test_admin_event_reset_confirmation_required`

#### `plugin/tests/unit/event/test_event_models.py`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_repr_method`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_locked_status_defaults`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_max_team_size_bounds`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_time_constraint_validation`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_time_both_or_neither_constraint`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_name_validation_edge_cases`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_description_length_limits`
*   `python -m pytest plugin/tests/unit/event/test_event_models.py::test_event_max_team_size_minimum_value`

#### `plugin/tests/unit/team/test_team_models.py`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_generate_invite_code_excludes_confusing_characters`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_invite_code_length_is_correct`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_invite_code_fallback_to_uuid_on_collision`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_invite_code_generation_uniqueness`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_member_count_hybrid_property`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_repr_method`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_locked_status_defaults`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_ranking_status_defaults`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_name_validation_edge_cases`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_invite_code_length_validation`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_member_role_enum_validation`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_member_repr_method`
*   `python -m pytest plugin/tests/unit/team/test_team_models.py::test_team_member_unique_constraint_logic`

#### `plugin/tests/unit/user/test_user_models.py`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_repr_method`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_team_for_event_logic`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_is_in_team_for_event_logic`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_participation_rate_calculation`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_stats_empty_data_handling`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_eligibility_logic`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_can_have_multiple_teams_across_events`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_cannot_have_multiple_teams_in_same_event`
*   `python -m pytest plugin/tests/unit/user/test_user_models.py::test_user_role_in_team`

#### `plugin/tests/unit/utils/test_api_responses.py`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_success_response_basic`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_success_response_with_custom_status`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_success_response_empty_data`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_success_response_filters_internal_fields`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_error_response_basic`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_error_response_with_custom_field`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_error_response_with_status_code`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_controller_response_success_result`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_controller_response_error_result`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_controller_response_with_custom_status`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_datetime_fields`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_none_value`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_model_object`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_enum_fields`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_nested_objects`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_list_of_objects`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_serialize_primitive_values`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_success_response_structure_consistency`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_error_response_structure_consistency`
*   `python -m pytest plugin/tests/unit/utils/test_api_responses.py::test_controller_response_routing`

#### `plugin/tests/unit/utils/test_data_conversion.py`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_rows_to_dicts_empty_input`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_rows_to_dicts_basic_conversion`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_rows_to_dicts_field_mapping`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_rows_to_dicts_with_none_values`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_row_to_dict_single_row`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_row_to_dict_with_nested_objects`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_row_to_dict_with_special_types`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_empty_fields_list`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_missing_attribute`
*   `python -m pytest plugin/tests/unit/utils/test_data_conversion.py::test_rows_with_different_fields`

#### `plugin/tests/unit/utils/test_validators.py`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_valid_team_creation`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_invalid_team_creation`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_valid_event_creation`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_invalid_event_creation`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_validate_string`
*   `python -m pytest plugin/tests/unit/utils/test_validators.py::test_validate_positive_integer`

#### `plugin/tests/unit/utils/test_validators_extended.py`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_datetime_validation_various_formats`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_datetime_validation_invalid_formats`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_datetime_past_validation`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_positive_integer_edge_values`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_positive_integer_invalid_types`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_string_length_validation_unicode`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_string_whitespace_handling`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_boolean_validation_string_inputs`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_boolean_validation_proper_types`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_confirmation_validation_case_sensitivity`
*   `python -m pytest plugin/tests/unit/utils/test_validators_extended.py::test_integer_range_boundaries`

---

### **Integration Tests (`tests/integration/`)**

#### `plugin/tests/integration/admin/test_admin_controllers.py`
*   `python -m pytest plugin/tests/integration/admin/test_admin_controllers.py::test_get_data_counts`
*   `python -m pytest plugin/tests/integration/admin/test_admin_controllers.py::test_cleanup_headless_teams`

#### `plugin/tests/integration/event/test_event_controllers.py`
*   `python -m pytest plugin/tests/integration/event/test_event_controllers.py::test_create_event_with_all_fields`

#### `plugin/tests/integration/event/test_event_lifecycle.py`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_creation_with_teams_cascade`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_locking_prevents_new_teams`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_max_team_size_update_validation`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_time_constraint_updates`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_deletion_cleanup_cascade`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_multi_event_scenario_isolation`
*   `python -m pytest plugin/tests/integration/event/test_event_lifecycle.py::test_event_listing_and_statistics`

#### `plugin/tests/integration/team/test_captain_edge_cases.py`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_removal_when_team_becomes_empty`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_removal_auto_promotion_order`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_transfer_validation_chain`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_headless_team_recovery_multiple_candidates`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_cannot_remove_themselves`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_succession_after_multiple_transfers`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_permissions_boundary_conditions`
*   `python -m pytest plugin/tests/integration/team/test_captain_edge_cases.py::test_captain_edge_case_with_locked_teams`

#### `plugin/tests/integration/team/test_complex_team_operations.py`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_team_full_lifecycle_single_transaction`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_concurrent_team_creation_race_conditions`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_team_member_limit_enforcement_edge_cases`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_captain_edge_case_recovery_scenarios`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_cross_event_team_isolation`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_invite_code_regeneration_workflow`
*   `python -m pytest plugin/tests/integration/team/test_complex_team_operations.py::test_admin_override_team_operations`

#### `plugin/tests/integration/team/test_team_controllers.py`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_create_team_sets_creator_as_captain`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_join_team_adds_member`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_leave_team_removes_member`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_captain_cannot_leave_team_with_members`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_transfer_captaincy`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_remove_member_by_captain`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_update_team_by_captain`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_disband_team_by_captain`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_list_teams_in_event`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_get_team_info`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_joining_full_team_fails`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_cannot_join_team_twice`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_cannot_join_multiple_teams_in_same_event`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_locked_event_prevents_team_creation`
*   `python -m pytest plugin/tests/integration/team/test_team_controllers.py::test_locked_team_prevents_joining`

#### `plugin/tests/integration/user/test_user_controllers.py`
*   `python -m pytest plugin/tests/integration/user/test_user_controllers.py::test_get_user_teams_across_events`

---

### **API Tests (`tests/api/`)**

#### `plugin/tests/api/admin/test_admin_api.py`
*   `python -m pytest plugin/tests/api/admin/test_admin_api.py::test_admin_endpoints_require_admin`
*   `python -m pytest plugin/tests/api/admin/test_admin_api.py::test_admin_endpoint_with_admin_user`

#### `plugin/tests/api/event/test_event_api.py`
*   `python -m pytest plugin/tests/api/event/test_event_api.py::test_events_endpoint_with_authentication`
*   `python -m pytest plugin/tests/api/event/test_event_api.py::test_create_event_is_forbidden_for_normal_user`
*   `python -m pytest plugin/tests/api/event/test_event_api.py::test_create_event_succeeds_for_admin_user`

#### `plugin/tests/api/team/test_team_api.py`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_teams_endpoint_requires_authentication`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_teams_endpoint_with_authentication`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_create_team_requires_data`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_create_team_creator_becomes_captain`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_captain_assignment_security`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_update_team_endpoint_security`
*   `python -m pytest plugin/tests/api/team/test_team_api.py::test_join_team_fails_if_already_in_a_team_in_event`

#### `plugin/tests/api/user/test_user_api.py`
*   `python -m pytest plugin/tests/api/user/test_user_api.py::test_users_me_teams_endpoint`
