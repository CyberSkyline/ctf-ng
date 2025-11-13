"""
Test cases for the Hint model to verify validation and database operations.
"""

import pytest

from ...core.exceptions import ValidationError
from ... import config
from ..models.Hint import Hint


@pytest.fixture
def valid_hint_data(challenge):
    """Valid hint data for testing."""
    return {
        "name": "HintName",
        "index": 0,
        "challenge_id": challenge.id,
        "body": "This is a helpful hint for solving the challenge",
        "preview": "Need a hint?",
        "deduction": 10,
    }


class Test_Validate:
    """Test validation logic for Hint model."""

    def test_validate_with_valid_data_should_pass(self, valid_hint_data):
        """Test that validation passes with valid data."""
        validated_data = Hint.validate(valid_hint_data)

        assert validated_data["challenge_id"] == valid_hint_data["challenge_id"]
        assert validated_data["body"] == valid_hint_data["body"]
        assert validated_data["preview"] == valid_hint_data["preview"]
        assert validated_data["deduction"] == valid_hint_data["deduction"]

    def test_validate_with_minimal_data_should_pass(self, challenge):
        """Test that validation passes with minimal required data."""
        minimal_data = {
            "name": "Hint 1",
            "challenge_id": challenge.id,
            "body": "Hint body",
            "deduction": 5,
            "index": 0,
        }

        validated_data = Hint.validate(minimal_data)

        assert validated_data["challenge_id"] == minimal_data["challenge_id"]
        assert validated_data["body"] == minimal_data["body"]
        assert validated_data["deduction"] == minimal_data["deduction"]

    def test_validate_missing_body_should_fail(self, valid_hint_data):
        """Test that validation fails when body is missing."""
        del valid_hint_data["body"]

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Body" in str(exc_info.value.errors)

    def test_validate_empty_body_should_fail(self, valid_hint_data):
        """Test that validation fails when body is empty."""
        valid_hint_data["body"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Body" in str(exc_info.value.errors)

    def test_validate_body_too_long_should_fail(self, valid_hint_data):
        """Test that validation fails when body exceeds maximum length."""
        valid_hint_data["body"] = "a" * (config.MAX_HINT_BODY_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Body" in str(exc_info.value.errors)

    def test_validate_preview_too_long_should_fail(self, valid_hint_data):
        """Test that validation fails when preview exceeds maximum length."""
        valid_hint_data["preview"] = "a" * (config.MAX_HINT_PREVIEW_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Preview" in str(exc_info.value.errors)

    def test_validate_missing_deduction_should_fail(self, valid_hint_data):
        """Test that validation fails when deduction is missing."""
        del valid_hint_data["deduction"]

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Deduction" in str(exc_info.value.errors)

    def test_validate_negative_deduction_should_fail(self, valid_hint_data):
        """Test that validation fails when deduction is negative."""
        valid_hint_data["deduction"] = -1

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Deduction" in str(exc_info.value.errors)

    def test_validate_zero_deduction_should_fail(self, valid_hint_data):
        """Test that validation fails when deduction is zero."""
        valid_hint_data["deduction"] = 0

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Hint Deduction" in str(exc_info.value.errors)

    def test_validate_missing_challenge_id_should_fail(self, valid_hint_data):
        """Test that validation fails when challenge_id is missing."""
        del valid_hint_data["challenge_id"]

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_negative_challenge_id_should_fail(self, valid_hint_data):
        """Test that validation fails when challenge_id is negative."""
        valid_hint_data["challenge_id"] = -1

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_zero_challenge_id_should_fail(self, valid_hint_data):
        """Test that validation fails when challenge_id is zero."""
        valid_hint_data["challenge_id"] = 0

        with pytest.raises(ValidationError) as exc_info:
            Hint.validate(valid_hint_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_with_empty_preview_should_pass(self, valid_hint_data):
        """Test that validation passes when preview is empty (optional field)."""
        valid_hint_data["preview"] = ""

        validated_data = Hint.validate(valid_hint_data)
        assert validated_data["preview"] == ""

    def test_validate_without_preview_should_pass(self, valid_hint_data):
        """Test that validation passes when preview is not provided (optional field)."""
        del valid_hint_data["preview"]

        validated_data = Hint.validate(valid_hint_data)
        assert "preview" not in validated_data or validated_data["preview"] is None


@pytest.mark.db
class Test_Create_Hint:
    """Test database operations for Hint model."""

    def test_create_hint_with_valid_data_should_succeed(self, db_session, valid_hint_data):
        """Test that creating a hint with valid data succeeds."""
        hint = Hint.create_hint(**valid_hint_data)

        assert hint.id is not None
        assert hint.challenge_id == valid_hint_data["challenge_id"]
        assert hint.body == valid_hint_data["body"]
        assert hint.preview == valid_hint_data["preview"]
        assert hint.deduction == valid_hint_data["deduction"]

    def test_create_hint_should_persist_to_database(self, db_session, valid_hint_data):
        """Test that created hint is properly persisted to database."""
        hint = Hint.create_hint(**valid_hint_data)

        # Retrieve from database
        retrieved_hint = Hint.query.get(hint.id)

        assert retrieved_hint is not None
        assert retrieved_hint.challenge_id == valid_hint_data["challenge_id"]
        assert retrieved_hint.body == valid_hint_data["body"]
        assert retrieved_hint.preview == valid_hint_data["preview"]
        assert retrieved_hint.deduction == valid_hint_data["deduction"]

    def test_create_hint_with_minimal_data_should_succeed(self, db_session, challenge):
        """Test that creating a hint with minimal data succeeds."""
        hint = Hint.create_hint(name="Hint Name", challenge_id=challenge.id, body="Simple hint", deduction=5, index=0)

        assert hint.id is not None
        assert hint.challenge_id == challenge.id
        assert hint.body == "Simple hint"
        assert hint.preview == ""  # Default value
        assert hint.deduction == 5

    def test_create_hint_with_invalid_data_should_fail(self, db_session, challenge):
        """Test that creating a hint with invalid data fails."""
        with pytest.raises(ValidationError):
            Hint.create_hint(
                name="Hint Name",
                challenge_id=challenge.id,
                body="",  # Invalid: empty body
                deduction=10,
                index=0,
            )

    def test_create_hint_should_rollback_on_validation_error(self, db_session, challenge):
        """Test that database rollback occurs when validation fails."""
        initial_count = Hint.query.count()

        with pytest.raises(ValidationError):
            Hint.create_hint(
                name="Hint Name",
                challenge_id=challenge.id,
                body="",  # Invalid: empty body
                deduction=10,
                index=0,
            )

        # Verify no hint was created
        assert Hint.query.count() == initial_count

    def test_create_hint_with_commit_false_should_not_commit(self, db_session, valid_hint_data):
        """Test that creating a hint with commit=False doesn't commit to database."""
        hint = Hint.create_hint(commit=False, **valid_hint_data)

        # Flush session to clear it
        db_session.flush()
        db_session.expunge_all()

        # Hint should exist in session but not committed
        assert hint.id is not None

        # After rollback, hint should not exist
        db_session.rollback()
        retrieved_hint = Hint.query.get(hint.id)
        assert retrieved_hint is None

    def test_hint_challenge_relationship_should_work(self, db_session, valid_hint_data, challenge):
        """Test that the relationship between Hint and Challenge works."""
        hint = Hint.create_hint(**valid_hint_data)

        # Test that hint has reference to challenge
        assert hint.challenge is not None
        assert hint.challenge.id == challenge.id
        assert hint.challenge.name == challenge.name

    def test_create_multiple_hints_for_same_challenge(self, db_session, challenge):
        """Test that multiple hints can be created for the same challenge."""
        # TODO: Why do it this way instead of just passing it in as keywords?
        hint1_data = {
            "name": "Hint 1",
            "challenge_id": challenge.id,
            "body": "First hint body",
            "preview": "Hint 1",
            "deduction": 5,
            "index": 0,
        }

        hint2_data = {
            "name": "Hint 2",
            "challenge_id": challenge.id,
            "body": "Second hint body",
            "preview": "Hint 2",
            "deduction": 10,
            "index": 1,
        }

        hint1 = Hint.create_hint(**hint1_data)
        hint2 = Hint.create_hint(**hint2_data)

        assert hint1.id != hint2.id
        assert hint1.challenge_id == hint2.challenge_id == challenge.id

        # Both hints should be retrievable
        assert Hint.query.get(hint1.id) is not None
        assert Hint.query.get(hint2.id) is not None

    def test_create_hint_with_different_deductions(self, db_session, challenge):
        """Test creating hints with different deduction values."""
        deduction_values = [1, 5, 10, 25, 50, 100]
        created_hints = []

        for i, deduction in enumerate(deduction_values):
            hint = Hint.create_hint(
                name="Name", challenge_id=challenge.id, body=f"Hint {i + 1} body", preview=f"Hint {i + 1}", deduction=deduction, index=i
            )
            created_hints.append(hint)

        # Verify all hints were created with correct deductions
        for hint, expected_deduction in zip(created_hints, deduction_values, strict=True):
            retrieved_hint = Hint.query.get(hint.id)
            assert retrieved_hint.deduction == expected_deduction

    def test_create_hint_with_maximum_length_fields(self, db_session, challenge):
        """Test creating hints with maximum allowed field lengths."""
        max_body = "a" * config.MAX_HINT_BODY_LENGTH
        max_preview = "b" * config.MAX_HINT_PREVIEW_LENGTH

        hint = Hint.create_hint(name="Name", challenge_id=challenge.id, body=max_body, preview=max_preview, deduction=15, index=0)

        assert hint.body == max_body
        assert hint.preview == max_preview
        assert len(hint.body) == config.MAX_HINT_BODY_LENGTH
        assert len(hint.preview) == config.MAX_HINT_PREVIEW_LENGTH

    def test_create_hint_with_special_characters(self, db_session, challenge):
        """Test creating hints with special characters in text fields."""
        special_body = "This hint contains special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_preview = "Special preview: ñáéíóú çüö"

        hint = Hint.create_hint(name="Hint Name", challenge_id=challenge.id, body=special_body, preview=special_preview, deduction=20, index=0)

        assert hint.body == special_body
        assert hint.preview == special_preview

        # Verify persistence
        retrieved_hint = Hint.query.get(hint.id)
        assert retrieved_hint.body == special_body
        assert retrieved_hint.preview == special_preview

    def test_create_hint_with_unicode_content(self, db_session, challenge):
        """Test creating hints with Unicode content."""
        unicode_body = "Hint with emoji: 🔍 and accents: café naïve résumé"
        unicode_preview = "Unicode: 中文 русский 日本語"

        hint = Hint.create_hint(name="Hint Name", challenge_id=challenge.id, body=unicode_body, preview=unicode_preview, deduction=8, index=0)

        assert hint.body == unicode_body
        assert hint.preview == unicode_preview

    def test_create_hint_with_newlines_and_whitespace(self, db_session, challenge):
        """Test creating hints with newlines and whitespace."""
        body_with_newlines = "Line 1\nLine 2\n\nLine 4\tTabbed content"
        preview_with_spaces = "  Spaced  preview  "

        hint = Hint.create_hint(
            name="Hint Name", challenge_id=challenge.id, body=body_with_newlines, preview=preview_with_spaces, deduction=12, index=0
        )

        # Validator strips leading and trailing whitespace
        assert hint.body == body_with_newlines.strip()
        assert hint.preview == preview_with_spaces.strip()

    def test_create_hint_with_minimum_positive_deduction(self, db_session, challenge):
        """Test creating hint with minimum positive deduction value."""
        hint = Hint.create_hint(
            name="Hint Name",
            challenge_id=challenge.id,
            body="Minimal deduction hint",
            deduction=1,  # Minimum positive value
            index=0,
        )

        assert hint.deduction == 1

    def test_create_hint_with_large_deduction_value(self, db_session, challenge):
        """Test creating hint with large deduction value."""
        large_deduction = 999999

        hint = Hint.create_hint(name="Hint Name", challenge_id=challenge.id, body="Expensive hint", deduction=large_deduction, index=0)

        assert hint.deduction == large_deduction
