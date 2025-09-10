"""
Test cases for the ChallengeTag model to verify validation and database operations.
"""

import pytest

from ...core.exceptions import ValidationError
from ..models.ChallengeTag import MAX_CHALLENGE_TAG_NAME_LENGTH, ChallengeTag


@pytest.fixture
def valid_challenge_tag_data(challenge):
    """Valid challenge tag data for testing."""
    return {
        "challenge_id": challenge.id,
        "name": "web",
    }


class TestChallengeTagValidation:
    """Test validation logic for ChallengeTag model."""

    def test_validate_with_valid_data_should_pass(self, valid_challenge_tag_data):
        """Test that validation passes with valid data."""
        validated_data = ChallengeTag.validate(valid_challenge_tag_data)

        assert validated_data["challenge_id"] == valid_challenge_tag_data["challenge_id"]
        assert validated_data["name"] == valid_challenge_tag_data["name"]

    def test_validate_missing_name_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when name is missing."""
        del valid_challenge_tag_data["name"]

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge Tag Name" in str(exc_info.value.errors)

    def test_validate_empty_name_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when name is empty."""
        valid_challenge_tag_data["name"] = ""

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge Tag Name" in str(exc_info.value.errors)

    def test_validate_name_too_long_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when name exceeds maximum length."""
        valid_challenge_tag_data["name"] = "a" * (MAX_CHALLENGE_TAG_NAME_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge Tag Name" in str(exc_info.value.errors)

    def test_validate_missing_challenge_id_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when challenge_id is missing."""
        del valid_challenge_tag_data["challenge_id"]

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_negative_challenge_id_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when challenge_id is negative."""
        valid_challenge_tag_data["challenge_id"] = -1

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_zero_challenge_id_should_fail(self, valid_challenge_tag_data):
        """Test that validation fails when challenge_id is zero."""
        valid_challenge_tag_data["challenge_id"] = 0

        with pytest.raises(ValidationError) as exc_info:
            ChallengeTag.validate(valid_challenge_tag_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_with_whitespace_name_should_pass(self, valid_challenge_tag_data):
        """Test that validation passes with name containing whitespace."""
        valid_challenge_tag_data["name"] = "web exploitation"

        validated_data = ChallengeTag.validate(valid_challenge_tag_data)

        assert validated_data["name"] == "web exploitation"

    def test_validate_with_special_characters_should_pass(self, valid_challenge_tag_data):
        """Test that validation passes with name containing special characters."""
        valid_challenge_tag_data["name"] = "web-app_security"

        validated_data = ChallengeTag.validate(valid_challenge_tag_data)

        assert validated_data["name"] == "web-app_security"

    def test_validate_with_numeric_name_should_pass(self, valid_challenge_tag_data):
        """Test that validation passes with numeric name."""
        valid_challenge_tag_data["name"] = "100"

        validated_data = ChallengeTag.validate(valid_challenge_tag_data)

        assert validated_data["name"] == "100"

    def test_validate_with_maximum_length_name_should_pass(self, valid_challenge_tag_data):
        """Test that validation passes with name at maximum length."""
        valid_challenge_tag_data["name"] = "a" * MAX_CHALLENGE_TAG_NAME_LENGTH

        validated_data = ChallengeTag.validate(valid_challenge_tag_data)

        assert len(validated_data["name"]) == MAX_CHALLENGE_TAG_NAME_LENGTH


class Test_Create_Tag:
    """Test database operations for ChallengeTag model."""

    def test_create_tag_with_valid_data_should_succeed(self, challenge):
        """Test that creating a tag with valid data succeeds."""
        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name="web", commit=False)

        assert tag is not None
        assert tag.challenge_id == challenge.id
        assert tag.name == "web"

    def test_create_tag_should_persist_to_database(self, challenge):
        """Test that created tag is persisted to the database."""
        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name="crypto", commit=True)

        # Query the database to verify persistence
        retrieved_tag = ChallengeTag.query.filter_by(id=tag.id).first()
        assert retrieved_tag is not None
        assert retrieved_tag.name == "crypto"
        assert retrieved_tag.challenge_id == challenge.id

    def test_create_tag_with_invalid_data_should_fail(self, challenge):
        """Test that creating a tag with invalid data fails."""
        with pytest.raises(ValidationError):
            ChallengeTag.create_tag(
                challenge_id=challenge.id,
                name="",  # Empty name should fail
                commit=False,
            )

    def test_create_tag_should_rollback_on_validation_error(self, challenge):
        """Test that database session is rolled back on validation error."""
        with pytest.raises(ValidationError):
            ChallengeTag.create_tag(
                challenge_id=-1,  # Invalid challenge_id
                name="test",
                commit=True,
            )

        # Verify no tag was created
        tags = ChallengeTag.query.filter_by(name="test").all()
        assert len(tags) == 0

    def test_challenge_tag_challenge_relationship_should_work(self, challenge):
        """Test that the relationship to Challenge works correctly."""
        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name="pwn", commit=True)

        # Test the relationship
        assert tag.challenge is not None
        assert tag.challenge.id == challenge.id
        assert tag.challenge.name == challenge.name

    def test_create_multiple_tags_for_same_challenge(self, challenge):
        """Test creating multiple tags for the same challenge."""
        tag1 = ChallengeTag.create_tag(challenge_id=challenge.id, name="web", commit=True)

        tag2 = ChallengeTag.create_tag(challenge_id=challenge.id, name="sql-injection", commit=True)

        assert tag1.challenge_id == tag2.challenge_id == challenge.id
        assert tag1.name != tag2.name

        # Verify both tags exist in database
        tags = ChallengeTag.query.filter_by(challenge_id=challenge.id).all()
        tag_names = [tag.name for tag in tags]
        assert "web" in tag_names
        assert "sql-injection" in tag_names

    def test_create_tag_with_different_challenge_ids(self, challenge, event):
        """Test creating tags with different challenge IDs."""
        # We only have one challenge fixture, so we'll test with different valid IDs
        tag1 = ChallengeTag.create_tag(challenge_id=challenge.id, name="misc", commit=True)

        # Create another challenge for testing
        from ..models.Challenge import Challenge

        challenge2 = Challenge.create_challenge(
            event_id=event.id,  # Use the same event
            name="Test Challenge 2",
            description="Another test challenge",
            commit=True,
            challenge_yaml="Initial Fake Data",  # TODO: Replace with actual data once round tripping is set up
        )

        tag2 = ChallengeTag.create_tag(challenge_id=challenge2.id, name="misc", commit=True)

        assert tag1.challenge_id != tag2.challenge_id
        assert tag1.name == tag2.name  # Same name, different challenges

    def test_create_tag_with_maximum_length_name(self, challenge):
        """Test creating a tag with maximum length name."""
        max_length_name = "a" * MAX_CHALLENGE_TAG_NAME_LENGTH

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=max_length_name, commit=True)

        assert len(tag.name) == MAX_CHALLENGE_TAG_NAME_LENGTH
        assert tag.name == max_length_name

    def test_create_tag_with_special_characters(self, challenge):
        """Test creating a tag with special characters in name."""
        special_name = "web-app_security!@#"

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=special_name, commit=True)

        assert tag.name == special_name

    def test_create_tag_with_unicode_name(self, challenge):
        """Test creating a tag with unicode characters in name."""
        unicode_name = "密码学"  # "Cryptography" in Chinese

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=unicode_name, commit=True)

        assert tag.name == unicode_name

    def test_create_tag_with_mixed_case_name(self, challenge):
        """Test creating a tag with mixed case name."""
        mixed_case_name = "WebApp"

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=mixed_case_name, commit=True)

        assert tag.name == mixed_case_name

    def test_create_tag_with_numbers_and_letters(self, challenge):
        """Test creating a tag with numbers and letters."""
        alphanumeric_name = "web2024"

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=alphanumeric_name, commit=True)

        assert tag.name == alphanumeric_name

    def test_create_tag_with_whitespace_edges(self, challenge):
        """Test creating a tag with whitespace at edges (should be handled by validation)."""
        name_with_spaces = " web "

        tag = ChallengeTag.create_tag(challenge_id=challenge.id, name=name_with_spaces, commit=True)

        # The validation should strip whitespace from the input
        assert tag.name == "web"
