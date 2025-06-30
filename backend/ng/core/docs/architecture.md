# CTF-NG Plugin Architecture

This document outlines the architectural patterns and engineering principles used throughout the CTF-NG plugin codebase.

## Overview

CTF-NG is a Flask plugin for CTFd that adds team management, event organization, and support ticket functionality. The codebase follows strict MVC principles adapted for a RESTful API architecture.

## Core Principles

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Explicit Over Implicit**: Clear function names, explicit imports, and obvious data flow
3. **Composition Over Inheritance**: Heavy use of decorators for composable functionality
4. **Database Encapsulation**: All database operations live in model methods

## Directory Structure

```
backend/ng/
├── core/               # Shared utilities and infrastructure
│   ├── middleware/     # Decorators for auth, permissions, resource loading
│   ├── validation/     # Input validation framework
│   └── utils/          # API responses, logging, serialization
├── event/              # Event domain
├── team/               # Team domain  
├── user/               # User domain
├── support/            # Support ticket domain
└── admin/              # Administrative operations
```

Each domain follows this structure:
- `models/` - SQLAlchemy models and ALL database operations
- `controllers/` - Business logic orchestration
- `routes/` - HTTP endpoint definitions

## Request Flow

A typical API request follows this flow:

```
HTTP Request
    ↓
Route Definition (@namespace.route)
    ↓
Middleware Stack (decorators)
    - Authentication (@user_endpoint, @admin_endpoint)
    - Input Validation (validation_func)
    - Resource Loading (@load_event, @load_team)
    - Permission Checks (@require_team_captain)
    ↓
Controller Function
    - Receives validated data from g.validated_data
    - Accesses loaded resources from g.event, g.team, etc.
    - Calls model methods for DB operations
    - Returns structured dict
    ↓
Response Serialization (success_response)
    ↓
HTTP Response
```

## Middleware System

### Authentication Decorators
```python
@api_endpoint()      # Base decorator with error handling
@user_endpoint()     # Requires authenticated user
@admin_endpoint()    # Requires admin privileges
@public_endpoint()   # No auth required
```

### Resource Loading
Resources are loaded into Flask's `g` object:
```python
@load_event()        # Loads g.event from event_id in URL
@load_team()         # Loads g.team from team_id in URL
@load_user()         # Loads g.target_user from user_id in URL
```

### Permission Checking
```python
@require_team_captain()       # Verifies user is team captain
@require_ticket_access()      # Verifies user can access ticket
```

### Decorator Composition
Decorators are designed to be stacked:
```python
@user_endpoint(json_required=True, validation_func=validate_team_creation)
@load_event_from_request()
@check_team_join_eligibility()
def create_team(self):
    # All validation, loading, and checks already done
    data = g.validated_data
    event = g.event
    # ... business logic
```

## Validation Framework

### BaseValidator
Provides reusable validation primitives:
- `validate_string()` - String validation with length limits
- `validate_positive_integer()` - Positive integer validation
- `validate_boolean()` - Boolean validation
- `validate_datetime()` - ISO datetime validation

### Domain Validators
Each domain has specific validators:
```python
# event/validation.py
def validate_event_creation(data: dict[str, Any]) -> dict[str, Any]:
    validator = BaseValidator()
    validator.validate_string(data, "name", EVENT_NAME_MAX_LENGTH, required=True)
    # ... more validations
    return validator.parsed_data  # Returns only valid, parsed data
```

### Cross-Domain Validation
Shared validation logic lives in `core/validation/resources.py`:
- `validate_unique_name()` - Ensures names are unique within scope
- `validate_team_capacity()` - Checks team size limits
- `validate_event_locked_state()` - Prevents operations on locked events

## Database Patterns

### Model Responsibilities
Models contain ALL database operations:
```python
class Team(db.Model):
    # Column definitions...
    
    @classmethod
    def create_team(cls, name, event_id, invite_code):
        """Create and persist a new team"""
        team = cls(name=name, event_id=event_id, invite_code=invite_code)
        db.session.add(team)
        db.session.commit()
        return team
```

### Transaction Management
Complex operations use transactions:
```python
def create_team_with_captain(cls, name, event_id, creator_id):
    try:
        team = cls.create_team(name, event_id, flush_only=True)
        TeamMember.create_team_member(creator_id, team.id, role=TeamRole.CAPTAIN)
        db.session.commit()
        return True, {"team": team}
    except IntegrityError:
        db.session.rollback()
        return False, {"error": "Team name already exists"}
```

### Query Patterns
- Use query methods, not raw queries
- Always terminate queries (`.all()`, `.first()`, `.scalar()`)
- Use hybrid properties for computed attributes
- Eager load relationships when needed to avoid N+1

## Error Handling

### Exception Hierarchy
```
APIException (base)
├── ValidationError (400) - Invalid input data
├── NotFoundError (404) - Resource doesn't exist
├── PermissionError (403) - Insufficient permissions
├── ConflictError (409) - Constraint violations
└── BusinessLogicError (400) - Business rule violations
```

### Global Error Handler
The `@handle_exceptions` decorator on every endpoint ensures:
- Proper database cleanup (`db.session.remove()`)
- Consistent error response format
- Appropriate logging

## API Response Format

### Success Response
```json
{
    "success": true,
    "data": {
        "team": {
            "id": 123,
            "name": "Team Alpha",
            "member_count": 4
        }
    }
}
```

### Error Response
```json
{
    "success": false,
    "errors": {
        "name": "Team name already exists in this event"
    }
}
```

## Serialization

Models implement `serialize()` method:
```python
def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
    data = {
        "id": self.id,
        "name": self.name,
        "member_count": self.member_count
    }
    if include_admin_fields:
        data["invite_code"] = self.invite_code
    return data
```

The `serialize_model_for_api()` utility handles:
- Recursive serialization
- DateTime formatting (ISO with 'Z' suffix)
- SQLAlchemy Row objects
- Enum value extraction

## Testing Strategy

Tests are organized by type:
- `test_*_models.py` - Model method tests (with DB)
- `test_*_controllers.py` - Business logic tests
- `test_*_api.py` - Full API endpoint tests

Key fixtures in `conftest.py`:
- `app` - Test application instance
- `db_session` - Isolated database session
- `logged_in_client` - Authenticated test client
- `admin_client` - Admin test client

## Common Patterns

### Loading User's Team in Event
```python
@load_user_team_in_event()  # Loads event, team_member, and team
def leave_team(self):
    team = g.team
    team_member = g.team_member
    # Business logic...
```

### Conditional Updates
```python
update_data = build_conditional_update_data(
    team,
    name=(new_name, new_name and new_name != team.name),
    locked=(locked, locked is not None)
)
if update_data:
    team.update(**update_data)
```

### Permission + Resource Loading
```python
@load_team()
@require_team_captain()
def update_team(self, team_id):
    # User is guaranteed to be team captain
    team = g.team
```

## Best Practices

1. **Controllers never touch db.session** - Always call model methods
2. **Validate early** - Use validation_func in decorators
3. **Load resources once** - Use middleware to load and reuse via `g`
4. **Explicit imports** - No star imports, clear module paths
5. **Fail fast** - Validate and check permissions before business logic
6. **Use enums** - Prevent magic strings (e.g., TeamRole.CAPTAIN)
7. **Transaction boundaries** - Clearly defined in model methods

## Adding New Features

When adding a new domain or feature:

1. Create domain folder with `models/`, `controllers/`, `routes/` structure
2. Define models with all DB operations as methods
3. Create validators in `core/validation/xyz_domain.py`
4. Implement controllers with business logic
5. Define routes using appropriate decorators
6. Add to main blueprint in `core/routes/__init__.py`
7. Write tests following existing patterns

## WebSocket Support (Future)

The support ticket system includes WebSocket infrastructure:
- Event emission via `emit_event()` utility
- Room-based broadcasting (e.g., `ticket_123`)
- Socket handlers in `support/sockets.py`

Currently disabled but ready for activation when needed
