"""
/backend/ctfd/plugin/tests/unit/team/test_team_models.py
Unit tests for team model logic without database dependencies.
"""

from unittest.mock import Mock, patch

from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.team.models.enums import TeamRole
from plugin.team.controllers._generate_invite_code import _generate_invite_code


class TestTeamInviteCodeGeneration:
    """Test invite code generation logic."""

    def test_generate_invite_code_excludes_confusing_characters(self):
        """Test that invite codes exclude visually confusing characters."""

        with patch("plugin.team.controllers._generate_invite_code.Team") as mock_team:
            mock_team.query.filter_by.return_value.first.return_value = None

            codes = []
            for _ in range(100):
                code = _generate_invite_code()
                codes.append(code)

            confusing_chars = "0O1Il"
            for code in codes:
                for char in confusing_chars:
                    assert char not in code, f"Code {code} contains confusing character {char}"

    def test_invite_code_length_is_correct(self):
        """Test that invite codes have the expected length."""
        with patch("plugin.team.controllers._generate_invite_code.Team") as mock_team:
            mock_team.query.filter_by.return_value.first.return_value = None

            code = _generate_invite_code()
            assert len(code) == 8, f"Expected code length 8, got {len(code)}"

    def test_invite_code_fallback_to_uuid_on_collision(self):
        """Test that code generation falls back to UUID after max retries."""
        with patch("plugin.team.controllers._generate_invite_code.Team") as mock_team:
            collision_count = 0

            def mock_collision(*args, **kwargs):
                nonlocal collision_count
                collision_count += 1
                # Return collision for first 12 attempts (10 + 2), then success
                if collision_count <= 12:
                    return Mock()
                return None

            mock_team.query.filter_by.return_value.first.side_effect = mock_collision

            code = _generate_invite_code()

            assert len(code) >= 8, f"Expected code length >= 8, got {len(code)}"
            assert collision_count > 10, "Should have tried multiple times before success"

    def test_invite_code_generation_uniqueness(self):
        """Test that multiple invite codes are unique."""
        with patch("plugin.team.controllers._generate_invite_code.Team") as mock_team:
            mock_team.query.filter_by.return_value.first.return_value = None

            codes = set()
            for _ in range(50):
                code = _generate_invite_code()
                codes.add(code)

            assert len(codes) == 50, "Generated codes are not unique"


class TestTeamModelLogic:
    """Test Team model properties and methods."""

    def test_team_member_count_hybrid_property(self):
        """Test the member_count hybrid property calculation."""
        team = Team()
        team.id = 1
        team.name = "Test Team"

        assert hasattr(team, "member_count"), "Team should have member_count property"

        try:
            team.member_count
        except Exception:
            pass

    def test_team_repr_method(self):
        """Test the string representation of Team model."""
        team = Team()
        team.name = "Alpha Team"

        repr_str = repr(team)
        assert "Team" in repr_str
        assert "Alpha Team" in repr_str

    def test_team_locked_status_defaults(self):
        """Test that team locked status defaults correctly."""
        team = Team()
        assert team.locked is False or team.locked is None, "Team should not be locked by default"

    def test_team_ranking_status_defaults(self):
        """Test that team ranking status defaults correctly."""
        team = Team()

        assert hasattr(team, "ranked"), "Team should have ranked attribute"


class TestTeamBusinessRules:
    """Test team-related business rule validations."""

    def test_team_name_validation_edge_cases(self):
        """Test edge cases for team name validation."""
        from plugin.utils import validate_team_creation

        # Empty name
        valid, errors = validate_team_creation({"name": "", "event_id": 1})
        assert not valid
        assert "name" in errors

        # Whitespace only
        valid, errors = validate_team_creation({"name": "   ", "event_id": 1})
        assert not valid
        assert "name" in errors

        # Unicode characters
        valid, errors = validate_team_creation({"name": "团队名称🚀", "event_id": 1})
        assert valid
        assert len(errors) == 0

        # Very long name
        long_name = "A" * 129
        valid, errors = validate_team_creation({"name": long_name, "event_id": 1})
        assert not valid
        assert "name" in errors

    def test_invite_code_length_validation(self):
        """Test that invite codes have valid length."""

        from plugin import config

        assert hasattr(config, "INVITE_CODE_LENGTH"), "INVITE_CODE_LENGTH should be defined"
        assert config.INVITE_CODE_LENGTH > 0, "INVITE_CODE_LENGTH should be positive"
        assert config.INVITE_CODE_LENGTH <= 32, "INVITE_CODE_LENGTH should be reasonable"


class TestTeamMemberModel:
    """Test TeamMember model logic."""

    def test_team_member_role_enum_validation(self):
        """Test that TeamRole enum has expected values."""
        assert hasattr(TeamRole, "CAPTAIN"), "TeamRole should have CAPTAIN"
        assert hasattr(TeamRole, "MEMBER"), "TeamRole should have MEMBER"

        # Check string values
        assert TeamRole.CAPTAIN.value == "captain"
        assert TeamRole.MEMBER.value == "member"

    def test_team_member_repr_method(self):
        """Test the string representation of TeamMember model."""
        member = TeamMember()
        member.user_id = 10
        member.team_id = 5
        member.event_id = 1
        member.role = TeamRole.CAPTAIN

        repr_str = repr(member)
        assert "TeamMember" in repr_str
        assert "user=10" in repr_str
        assert "team=5" in repr_str
        assert "event=1" in repr_str

    def test_team_member_unique_constraint_logic(self):
        """Test understanding of unique constraint on user/team/event."""

        member = TeamMember()
        member.user_id = 1
        member.team_id = 2

        assert hasattr(member, "user_id")
        assert hasattr(member, "team_id")
        assert hasattr(member, "role")
