"""
Test cases for Challenge model validation and functionality.
"""

import pytest

from ...core.exceptions import ValidationError
from ..models.Challenge import (
    MAX_CHALLENGE_DESCRIPTION_LENGTH,
    MAX_CHALLENGE_ICON_LENGTH,
    MAX_CHALLENGE_NAME_LENGTH,
    MAX_CHALLENGE_SUMMARY_LENGTH,
    Challenge,
)


@pytest.fixture
def challenge_data():
    """Provide valid challenge data for testing."""
    return {
        "name": "Test Challenge",
        "description": "A comprehensive test challenge description",
        "icon": "challenge-icon",
        "summary": "Challenge summary for testing",
    }


class TestChallengeValidation:
    """Test Challenge model validation logic."""

    def test_validate_with_valid_data_should_pass(self, challenge_data):
        """Test that valid challenge data passes validation."""
        validated_data = Challenge.validate(challenge_data)

        assert "name" in validated_data
        assert validated_data["name"] == challenge_data["name"]
        assert "description" in validated_data
        assert validated_data["description"] == challenge_data["description"]

    def test_validate_missing_name_should_fail(self, challenge_data):
        """Test that missing name field fails validation."""
        del challenge_data["name"]

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "name" in exc_info.value.errors
        assert "required" in exc_info.value.errors["name"].lower()

    def test_validate_empty_name_should_fail(self, challenge_data):
        """Test that empty name field fails validation."""
        challenge_data["name"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "name" in exc_info.value.errors
        assert "required" in exc_info.value.errors["name"].lower()

    def test_validate_whitespace_only_name_should_fail(self, challenge_data):
        """Test that whitespace-only name fails validation."""
        challenge_data["name"] = "   \t   \n   "

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "name" in exc_info.value.errors
        assert "empty" in exc_info.value.errors["name"].lower()

    def test_validate_name_too_long_should_fail(self, challenge_data):
        """Test that overly long name fails validation."""
        challenge_data["name"] = "a" * (MAX_CHALLENGE_NAME_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "name" in exc_info.value.errors
        assert "longer than" in exc_info.value.errors["name"].lower()

    def test_validate_description_too_long_should_fail(self, challenge_data):
        """Test that overly long description fails validation."""
        challenge_data["description"] = "a" * (MAX_CHALLENGE_DESCRIPTION_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "description" in exc_info.value.errors
        assert "longer than" in exc_info.value.errors["description"].lower()

    def test_validate_icon_too_long_should_fail(self, challenge_data):
        """Test that overly long icon fails validation."""
        challenge_data["icon"] = "a" * (MAX_CHALLENGE_ICON_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "icon" in exc_info.value.errors
        assert "longer than" in exc_info.value.errors["icon"].lower()

    def test_validate_summary_too_long_should_fail(self, challenge_data):
        """Test that overly long summary fails validation."""
        challenge_data["summary"] = "a" * (MAX_CHALLENGE_SUMMARY_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Challenge.validate(challenge_data)

        assert "summary" in exc_info.value.errors
        assert "longer than" in exc_info.value.errors["summary"].lower()

    def test_validate_with_whitespace_name_should_pass(self, challenge_data):
        """Test that names with leading/trailing whitespace are trimmed."""
        challenge_data["name"] = "  Valid Challenge Name  "

        validated_data = Challenge.validate(challenge_data)

        assert validated_data["name"] == "Valid Challenge Name"

    def test_validate_with_special_characters_should_pass(self, challenge_data):
        """Test that names with special characters pass validation."""
        special_names = [
            "Challenge #1",
            "Web-App Security",
            "Binary_Analysis",
            "Crypto & Forensics",
            "Network (Advanced)",
            "RE [Hard]",
            "PWN@2024",
        ]

        for name in special_names:
            challenge_data["name"] = name
            validated_data = Challenge.validate(challenge_data)
            assert validated_data["name"] == name

    def test_validate_with_unicode_name_should_pass(self, challenge_data):
        """Test that names with unicode characters pass validation."""
        unicode_names = [
            "チャレンジ 2024",
            "Défi Sécurité",
            "Безопасность",
            "挑战题目",
            "🔐 Crypto Challenge 🔐",
        ]

        for name in unicode_names:
            challenge_data["name"] = name
            validated_data = Challenge.validate(challenge_data)
            assert validated_data["name"] == name

    def test_validate_with_maximum_length_name_should_pass(self, challenge_data):
        """Test that maximum length name passes validation."""
        challenge_data["name"] = "a" * MAX_CHALLENGE_NAME_LENGTH

        validated_data = Challenge.validate(challenge_data)

        assert len(validated_data["name"]) == MAX_CHALLENGE_NAME_LENGTH

    def test_validate_optional_fields_missing_should_pass(self):
        """Test that validation passes when optional fields are missing."""
        minimal_data = {"name": "Minimal Challenge"}

        validated_data = Challenge.validate(minimal_data)

        assert validated_data["name"] == "Minimal Challenge"
        assert "description" not in validated_data
        assert "icon" not in validated_data
        assert "summary" not in validated_data

    def test_validate_optional_fields_empty_should_pass(self, challenge_data):
        """Test that validation passes when optional fields are empty."""
        challenge_data["description"] = ""
        challenge_data["icon"] = ""
        challenge_data["summary"] = ""

        validated_data = Challenge.validate(challenge_data)

        assert validated_data["name"] == challenge_data["name"]
        # Empty strings should not be included in validated data
        assert "description" not in validated_data or validated_data["description"] == ""
        assert "icon" not in validated_data or validated_data["icon"] == ""
        assert "summary" not in validated_data or validated_data["summary"] == ""

    def test_validate_optional_fields_whitespace_only_should_pass(self, challenge_data):
        """Test that validation passes when optional fields contain only whitespace."""
        challenge_data["description"] = "   \t   "
        challenge_data["icon"] = "  \n  "
        challenge_data["summary"] = "\t\t\t"

        validated_data = Challenge.validate(challenge_data)

        assert validated_data["name"] == challenge_data["name"]
        # Whitespace should be trimmed for optional fields

    def test_validate_with_maximum_length_fields(self):
        """Test validation with maximum length field values."""
        max_data = {
            "name": "a" * MAX_CHALLENGE_NAME_LENGTH,
            "description": "b" * MAX_CHALLENGE_DESCRIPTION_LENGTH,
            "icon": "c" * MAX_CHALLENGE_ICON_LENGTH,
            "summary": "d" * MAX_CHALLENGE_SUMMARY_LENGTH,
        }

        validated_data = Challenge.validate(max_data)

        assert len(validated_data["name"]) == MAX_CHALLENGE_NAME_LENGTH
        assert len(validated_data["description"]) == MAX_CHALLENGE_DESCRIPTION_LENGTH
        assert len(validated_data["icon"]) == MAX_CHALLENGE_ICON_LENGTH
        assert len(validated_data["summary"]) == MAX_CHALLENGE_SUMMARY_LENGTH

    def test_validate_with_unicode_content(self):
        """Test validation with unicode content."""
        unicode_data = {
            "name": "Unicode チャレンジ",
            "description": "This challenge contains 🔐 unicode characters и кириллицу",
            "icon": "🎯",
            "summary": "Résumé avec caractères spéciaux",
        }

        validated_data = Challenge.validate(unicode_data)

        assert validated_data["name"] == unicode_data["name"]
        assert validated_data["description"] == unicode_data["description"]
        assert validated_data["icon"] == unicode_data["icon"]
        assert validated_data["summary"] == unicode_data["summary"]

    def test_validate_with_mixed_case_name(self):
        """Test validation with mixed case name."""
        mixed_case_names = [
            "CamelCaseChallenge",
            "snake_case_challenge",
            "kebab-case-challenge",
            "MiXeD_CaSe-Challenge",
        ]

        for name in mixed_case_names:
            data = {"name": name}
            validated_data = Challenge.validate(data)
            assert validated_data["name"] == name

    def test_validate_with_numbers_and_letters(self):
        """Test validation with alphanumeric names."""
        alphanumeric_names = [
            "Challenge1",
            "Web101",
            "Crypto2024",
            "Binary4nalysis",
            "N3tw0rk1ng",
        ]

        for name in alphanumeric_names:
            data = {"name": name}
            validated_data = Challenge.validate(data)
            assert validated_data["name"] == name

    def test_validate_with_whitespace_edges(self):
        """Test validation with whitespace at edges of fields."""
        whitespace_data = {
            "name": "  Challenge Name  ",
            "description": "  Description with edges  ",
            "icon": "  icon  ",
            "summary": "  Summary content  ",
        }

        validated_data = Challenge.validate(whitespace_data)

        # Whitespace should be trimmed during validation
        assert validated_data["name"] == "Challenge Name"
        assert validated_data["description"] == "Description with edges"
        assert validated_data["icon"] == "icon"
        assert validated_data["summary"] == "Summary content"


class TestChallengeEdgeCases:
    """Test Challenge model edge cases and error scenarios."""

    def test_challenge_with_newlines_in_description(self):
        """Test challenge with multiline description."""
        multiline_description = """This is a challenge description
        that spans multiple lines
        and includes various formatting.

        It has:
        - Line breaks
        - Empty lines
        - Various whitespace"""

        data = {"name": "Multiline Challenge", "description": multiline_description}

        validated_data = Challenge.validate(data)
        assert validated_data["description"] == multiline_description

    def test_challenge_with_html_like_content(self):
        """Test challenge with HTML-like content in fields."""
        html_data = {
            "name": "Challenge <script>alert('xss')</script>",
            "description": "<p>This looks like HTML but should be treated as text</p>",
            "summary": "<div>Summary with tags</div>",
        }

        validated_data = Challenge.validate(html_data)

        # Content should be stored as-is (no HTML parsing/escaping in model)
        assert validated_data["name"] == html_data["name"]
        assert validated_data["description"] == html_data["description"]
        assert validated_data["summary"] == html_data["summary"]

    def test_challenge_with_sql_injection_like_content(self):
        """Test challenge with SQL injection-like content."""
        sql_data = {
            "name": "Challenge'; DROP TABLE challenges; --",
            "description": "Description with ' OR 1=1 --",
        }

        validated_data = Challenge.validate(sql_data)

        # Content should be stored safely
        assert validated_data["name"] == sql_data["name"]
        assert validated_data["description"] == sql_data["description"]

    def test_challenge_with_very_long_words(self):
        """Test challenge with very long words (no spaces)."""
        long_word = "a" * (MAX_CHALLENGE_NAME_LENGTH - 10)
        data = {"name": f"Test{long_word}"}

        validated_data = Challenge.validate(data)
        assert len(validated_data["name"]) <= MAX_CHALLENGE_NAME_LENGTH

    def test_challenge_validation_with_none_values(self):
        """Test challenge validation when None is passed for optional fields."""
        data = {"name": "Test Challenge", "description": None, "icon": None, "summary": None}

        # None values should be handled gracefully by the validator
        validated_data = Challenge.validate(data)
        assert validated_data["name"] == "Test Challenge"
