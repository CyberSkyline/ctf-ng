"""
Unit tests for user domain validation
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class TestUserValidation:
    """Test user validation logic."""

    def test_user_stats_validation(self):
        """Test user statistics validation."""

        def validate_user_stats(stats):
            errors = []

            required_fields = ["team_count", "events_participated", "challenges_solved"]
            for field in required_fields:
                if field not in stats:
                    errors.append(f"{field} is required")
                elif not isinstance(stats[field], int) or stats[field] < 0:
                    errors.append(f"{field} must be a non-negative integer")

            return errors

        valid_stats = {
            "team_count": 3,
            "events_participated": 5,
            "challenges_solved": 12,
        }
        invalid_stats = {"team_count": -1, "events_participated": "five"}

        assert validate_user_stats(valid_stats) == []
        errors = validate_user_stats(invalid_stats)
        assert len(errors) > 0
        assert any("challenges_solved is required" in error for error in errors)

    def test_user_eligibility_validation(self):
        """Test user team eligibility validation."""

        def validate_team_eligibility(user_data, event_data):
            errors = []

            if user_data.get("banned", False):
                errors.append("Banned users cannot join teams")

            current_teams = user_data.get("current_teams_in_event", 0)
            if current_teams >= 1:
                errors.append("User already has a team in this event")

            if event_data.get("registration_closed", False):
                errors.append("Event registration is closed")

            return len(errors) == 0, errors

        valid_user = {"banned": False, "current_teams_in_event": 0}
        valid_event = {"registration_closed": False}

        banned_user = {"banned": True, "current_teams_in_event": 0}
        closed_event = {"registration_closed": True}

        assert validate_team_eligibility(valid_user, valid_event)[0] is True
        assert validate_team_eligibility(banned_user, valid_event)[0] is False
        assert validate_team_eligibility(valid_user, closed_event)[0] is False


class TestUserProfileValidation:
    """Test user profile validation using BaseValidator framework."""

    def test_username_validation(self):
        """Test username validation rules."""
        from ...core.validation.framework import BaseValidator

        def validate_username(data):
            validator = BaseValidator()
            validator.validate_string(data, "username", max_length=50, required=True, friendly_name="Username")

            username = data.get("username", "").strip()
            if username and len(username) < 3:
                validator.errors["username"] = "Username must be at least 3 characters long"
            if username and not username.replace("_", "").replace("-", "").isalnum():
                validator.errors["username"] = "Username can only contain letters, numbers, underscores, and hyphens"

            return validator.is_valid()

        valid_cases = [
            {"username": "user123"},
            {"username": "test_user"},
            {"username": "user-name"},
            {"username": "ValidUser123"},
        ]

        for case in valid_cases:
            is_valid, errors, data = validate_username(case)
            assert is_valid, f"Expected {case} to be valid, got errors: {errors}"

        invalid_cases = [
            {"username": ""},  # Empty
            {"username": "ab"},  # Too short
            {"username": "user@name"},  # Invalid chars
            {"username": "user name"},  # Spaces
            {"username": "a" * 51},  # Too long
        ]

        for case in invalid_cases:
            is_valid, errors, data = validate_username(case)
            assert not is_valid, f"Expected {case} to be invalid"

    def test_email_validation(self):
        """Test email validation rules."""
        from ...core.validation.framework import BaseValidator
        import re

        def validate_email(data):
            validator = BaseValidator()
            validator.validate_string(data, "email", max_length=254, required=True, friendly_name="Email")

            email = data.get("email", "").strip()
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if email and not re.match(email_regex, email):
                validator.errors["email"] = "Email must be a valid email address"

            return validator.is_valid()

        valid_emails = [
            {"email": "user@example.com"},
            {"email": "test.user+tag@domain.co.uk"},
            {"email": "user123@test-domain.org"},
        ]

        for case in valid_emails:
            is_valid, errors, data = validate_email(case)
            assert is_valid, f"Expected {case} to be valid, got errors: {errors}"

        invalid_emails = [
            {"email": ""},  # Empty
            {"email": "notanemail"},  # No @
            {"email": "user@"},  # No domain
            {"email": "@domain.com"},  # No user
            {"email": "user@domain"},  # No TLD
        ]

        for case in invalid_emails:
            is_valid, errors, data = validate_email(case)
            assert not is_valid, f"Expected {case} to be invalid"

    def test_profile_completion_validation(self):
        """Test profile completion scoring validation."""

        def validate_profile_completion(data):
            errors = []
            completion_score = 0

            # Required fields (40% of score)
            required_fields = ["username", "email"]
            for field in required_fields:
                if data.get(field):
                    completion_score += 20
                else:
                    errors.append(f"{field} is required for profile completion")

            # Optional fields (60% of score)
            optional_fields = ["bio", "website", "twitter", "github", "discord"]
            filled_optional = sum(1 for field in optional_fields if data.get(field))
            completion_score += (filled_optional / len(optional_fields)) * 60

            return {
                "completion_score": round(completion_score, 1),
                "is_complete": completion_score >= 80,
                "missing_fields": errors,
            }

        # Minimal profile
        minimal_profile = {"username": "testuser", "email": "test@example.com"}
        result = validate_profile_completion(minimal_profile)
        assert result["completion_score"] == 40.0
        assert not result["is_complete"]

        # Complete profile
        complete_profile = {
            "username": "testuser",
            "email": "test@example.com",
            "bio": "Developer",
            "website": "https://example.com",
            "twitter": "@testuser",
            "github": "testuser",
            "discord": "testuser#1234",
        }
        result = validate_profile_completion(complete_profile)
        assert result["completion_score"] == 100.0
        assert result["is_complete"]

    def test_user_registration_validation(self):
        """Test comprehensive user registration validation."""
        from ...core.validation.framework import BaseValidator

        def validate_user_registration(data):
            validator = BaseValidator()

            # Required fields
            validator.validate_string(data, "username", max_length=50, required=True)
            validator.validate_string(data, "email", max_length=254, required=True)
            validator.validate_string(data, "password", required=True)
            validator.validate_string(data, "password_confirm", required=True)

            # Password strength validation
            password = data.get("password", "")
            if password and len(password) < 8:
                validator.errors["password"] = "Password must be at least 8 characters long"
            if password and not any(c.isupper() for c in password):
                validator.errors["password"] = "Password must contain at least one uppercase letter"
            if password and not any(c.islower() for c in password):
                validator.errors["password"] = "Password must contain at least one lowercase letter"
            if password and not any(c.isdigit() for c in password):
                validator.errors["password"] = "Password must contain at least one number"

            # Password confirmation
            if data.get("password") != data.get("password_confirm"):
                validator.errors["password_confirm"] = "Passwords do not match"

            # Terms acceptance
            validator.validate_boolean(data, "accept_terms", required=True, friendly_name="Terms acceptance")

            return validator.is_valid()

        # Valid registration
        valid_registration = {
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
            "accept_terms": True,
        }

        is_valid, errors, data = validate_user_registration(valid_registration)
        assert is_valid, f"Expected valid registration, got errors: {errors}"

        # Invalid registration - weak password
        weak_password = {
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "weak",
            "password_confirm": "weak",
            "accept_terms": True,
        }

        is_valid, errors, data = validate_user_registration(weak_password)
        assert not is_valid
        assert "password" in errors
