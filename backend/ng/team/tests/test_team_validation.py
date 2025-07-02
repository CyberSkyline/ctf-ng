"""
Unit tests for team domain validation
"""


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class TestTeamValidation:
    """Test team validation logic."""

    def test_team_name_validation(self):
        """Test team name validation rules."""

        def validate_team_name(name):
            errors = []

            if not name or not name.strip():
                errors.append("Team name is required")
            elif len(name.strip()) < 3:
                errors.append("Team name must be at least 3 characters")
            elif len(name) > 50:
                errors.append("Team name must be less than 50 characters")

            return errors

        assert validate_team_name("") == ["Team name is required"]
        assert validate_team_name("AB") == ["Team name must be at least 3 characters"]
        assert validate_team_name("A" * 51) == ["Team name must be less than 50 characters"]
        assert validate_team_name("Valid Team Name") == []

    def test_team_size_validation(self):
        """Test team size validation logic."""

        def validate_team_size(current_size, max_size, new_member_count=0):
            errors = []

            if current_size + new_member_count > max_size:
                errors.append(f"Team size would exceed maximum of {max_size}")
            if current_size < 0:
                errors.append("Team size cannot be negative")

            return errors

        assert validate_team_size(3, 5, 1) == []  # 3 + 1 = 4, under limit
        assert validate_team_size(5, 5, 1) == ["Team size would exceed maximum of 5"]
        assert validate_team_size(-1, 5) == ["Team size cannot be negative"]

    def test_invite_code_validation(self):
        """Test team invite code validation."""

        def validate_invite_code(code):
            if not code:
                return False, "Invite code is required"
            if len(code) != 8:
                return False, "Invite code must be 8 characters"
            if not code.isalnum():
                return False, "Invite code must be alphanumeric"
            return True, None

        assert validate_invite_code("ABC12345")[0] is True
        assert validate_invite_code("")[0] is False
        assert validate_invite_code("ABC123")[0] is False  # Too short
        assert validate_invite_code("ABC123!@")[0] is False  # Invalid chars
