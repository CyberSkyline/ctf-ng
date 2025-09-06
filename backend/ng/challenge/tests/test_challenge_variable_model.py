"""
Test cases for the ChallengeVariable model: validation, creation, relationships, and template usage.
"""
import pytest
import re
from ...core.exceptions import ValidationError
from ..models.ChallengeVariable import ChallengeVariable, MAX_VARIABLE_NAME_LENGTH, MAX_VARIABLE_DEFAULT_LENGTH, MAX_VARIABLE_TEMPLATE_LENGTH
from ..models import Challenge



@pytest.fixture
def valid_variable_data(challenge):
        """Valid variable data for testing."""
        return {
            "name": "test_var",
            "default": "default_value",
            "template": "Hello, {{name}}!",
            "challenge_id": challenge.id,
        }


@pytest.mark.parametrize(
        "field, value, error_msg",
        [
            ("name", "", "Variable Name"),
            ("name", "a" * (MAX_VARIABLE_NAME_LENGTH + 1), "Variable Name"),
            ("default", "", "Variable Default"),
            ("default", "a" * (MAX_VARIABLE_DEFAULT_LENGTH + 1), "Variable Default"),
            ("template", "", "Variable Template"),
            ("template", "a" * (MAX_VARIABLE_TEMPLATE_LENGTH + 1), "Variable Template"),
            ("challenge_id", None, "Challenge ID"),
        ]
)
def test_validate_invalid_data(field, value, error_msg, valid_variable_data):
        """Test that validation fails for invalid data."""
        data = valid_variable_data.copy()
        data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            ChallengeVariable.validate(data)
        assert error_msg in str(exc_info.value.errors)


def test_validate_valid_data(valid_variable_data):
    """Test that validation passes for valid data."""
    validated = ChallengeVariable.validate(valid_variable_data)
    for k, v in valid_variable_data.items():
        assert validated[k] == v


@pytest.mark.db
def test_create_variable_persists(db_session, valid_variable_data):
    """Test that a variable is created and persisted in the database."""
    variable = ChallengeVariable.create_variable(**valid_variable_data)
    assert variable.id is not None
    assert variable.name == valid_variable_data["name"]
    assert variable.default == valid_variable_data["default"]
    assert variable.template == valid_variable_data["template"]
    assert variable.challenge_id == valid_variable_data["challenge_id"]
    # Check retrieval
    retrieved = ChallengeVariable.query.get(variable.id)
    assert retrieved is not None
    assert retrieved.name == variable.name


@pytest.mark.db
def test_create_variable_invalid_rollback(db_session, challenge):
    """Test that invalid variable creation rolls back the session."""
    initial_count = ChallengeVariable.query.count()
    with pytest.raises(ValidationError):
        ChallengeVariable.create_variable(challenge_id=challenge.id, name="", default="default", template="template")
    assert ChallengeVariable.query.count() == initial_count


@pytest.mark.db
def test_variable_challenge_relationship(db_session, valid_variable_data, challenge):
    """Test that the relationship between ChallengeVariable and Challenge works."""
    variable = ChallengeVariable.create_variable(**valid_variable_data)
    assert variable.challenge is not None
    assert variable.challenge.id == challenge.id
    assert variable.challenge.name == challenge.name


@pytest.mark.db
def test_variable_questions_relationship(db_session, valid_variable_data, challenge):
    """Test that the questions relationship is empty by default."""
    variable = ChallengeVariable.create_variable(**valid_variable_data)
    assert hasattr(variable, "questions")
    assert variable.questions == []

faker_templates = [
    ("fake.password(length=12)", "db_password", r"^.{12}$"),
    ("fake.uuid4()", "session_id", r"^[0-9a-fA-F\-]{36}$"),
    ("fake.bothify('CTF{????-####}', letters='ABCDEF')", "flag-template", r"^CTF\{[A-F\?]{4}-\d{4}\}$"),
]

@pytest.mark.db
@pytest.mark.parametrize("template,name,pattern", faker_templates)
@pytest.mark.parametrize("seed", [42, 12345, 987654321])
def test_template_eval_faker_code(db_session, challenge, template, name, pattern, seed):
    """Test that template.eval(seed) works for Faker code snippets."""
    variable = ChallengeVariable.create_variable(
        challenge_id=challenge.id,
        name=name,
        default="default",
        template=template
    )
    attr = variable.as_attr()
    value = attr.template.eval(seed)
    assert isinstance(value, str)
    assert re.match(pattern, value)



# Test invalid faker templates raise on eval
invalid_faker_templates = [
    ("fake.nonexistent_method()", "bad_var"),
    ("fake.password(length='not_an_int')", "bad_var"),
]

@pytest.mark.db
@pytest.mark.parametrize("template,name", invalid_faker_templates)
@pytest.mark.parametrize("seed", [42])
def test_template_eval_invalid_faker_code_raises(db_session, challenge, template, name, seed):
    """Test that invalid faker code in template raises Exception on eval."""
    variable = ChallengeVariable.create_variable(
        challenge_id=challenge.id,
        name=name,
        default="default",
        template=template
    )
    # as_attr may raise during Template validation; accept that as a pass.
    try:
        attr = variable.as_attr()
    except Exception:
        # Validation failed as expected for invalid templates
        return

    # If as_attr succeeded, eval should raise for these invalid templates
    with pytest.raises(Exception):  # noqa: B017
        attr.template.eval(seed)
