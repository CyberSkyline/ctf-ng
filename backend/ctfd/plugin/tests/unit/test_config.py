"""
plugin/tests/unit/test_config.py
Sanity checks for the plugin's config values
"""

from plugin.config import (
    DEFAULT_TEAM_SIZE,
    MIN_TEAM_SIZE,
    MAX_TEAM_SIZE,
    INVITE_CODE_GENERATION_ATTEMPTS,
    INVITE_CODE_LENGTH,
    TEAM_NAME_MAX_LENGTH,
    WORLD_NAME_MAX_LENGTH,
    WORLD_DESCRIPTION_MAX_LENGTH,
    TEAM_ROLE_MAX_LENGTH,
    INVITE_CODE_MAX_LENGTH,
    EMPTY_TEAMS_WARNING_THRESHOLD,
    ADMIN_RESET_CONFIRMATION,
    ADMIN_WORLD_RESET_CONFIRMATION,
)


class TestConfig:
    """Tests for config values."""

    def test_default_team_size(self):
        """Check that default team size is valid."""
        assert isinstance(DEFAULT_TEAM_SIZE, int)
        assert DEFAULT_TEAM_SIZE > 0
        assert DEFAULT_TEAM_SIZE <= MAX_TEAM_SIZE
        assert DEFAULT_TEAM_SIZE <= 10

    def test_max_team_size(self):
        """Check that max team size is valid."""
        assert isinstance(MAX_TEAM_SIZE, int)
        assert MAX_TEAM_SIZE > 0
        assert MAX_TEAM_SIZE <= 20

    def test_invite_code_generation_attempts(self):
        """Check that the number of invite code generation attempts is reasonable."""
        assert isinstance(INVITE_CODE_GENERATION_ATTEMPTS, int)
        assert 5 <= INVITE_CODE_GENERATION_ATTEMPTS <= 20

    def test_min_team_size(self):
        """Check that min team size is valid."""
        assert isinstance(MIN_TEAM_SIZE, int)
        assert MIN_TEAM_SIZE > 0
        assert MIN_TEAM_SIZE <= DEFAULT_TEAM_SIZE
        assert MIN_TEAM_SIZE <= MAX_TEAM_SIZE

    def test_invite_code_length(self):
        """Check that invite code length is reasonable."""
        assert isinstance(INVITE_CODE_LENGTH, int)
        assert 4 <= INVITE_CODE_LENGTH <= 16

    def test_database_field_lengths(self):
        """Check that database field max lengths are reasonable."""
        assert isinstance(TEAM_NAME_MAX_LENGTH, int)
        assert 50 <= TEAM_NAME_MAX_LENGTH <= 500

        assert isinstance(WORLD_NAME_MAX_LENGTH, int)
        assert 100 <= WORLD_NAME_MAX_LENGTH <= 500

        assert isinstance(WORLD_DESCRIPTION_MAX_LENGTH, int)
        assert 500 <= WORLD_DESCRIPTION_MAX_LENGTH <= 5000

        assert isinstance(TEAM_ROLE_MAX_LENGTH, int)
        assert 20 <= TEAM_ROLE_MAX_LENGTH <= 100

        assert isinstance(INVITE_CODE_MAX_LENGTH, int)
        assert 16 <= INVITE_CODE_MAX_LENGTH <= 64

    def test_empty_teams_warning_threshold(self):
        """Check that empty teams warning threshold is a valid percentage."""
        assert isinstance(EMPTY_TEAMS_WARNING_THRESHOLD, (int, float))
        assert 0.0 <= EMPTY_TEAMS_WARNING_THRESHOLD <= 1.0

    def test_admin_confirmation_strings(self):
        """Check that admin confirmation strings are non empty."""
        assert isinstance(ADMIN_RESET_CONFIRMATION, str)
        assert len(ADMIN_RESET_CONFIRMATION) > 0
        assert ADMIN_RESET_CONFIRMATION.startswith("--")

        assert isinstance(ADMIN_WORLD_RESET_CONFIRMATION, str)
        assert len(ADMIN_WORLD_RESET_CONFIRMATION) > 0
        assert ADMIN_WORLD_RESET_CONFIRMATION.startswith("--")

    def test_team_size_constraints_are_logical(self):
        """Ensure team size values have logical relationships."""
        assert MIN_TEAM_SIZE <= DEFAULT_TEAM_SIZE <= MAX_TEAM_SIZE
        assert MIN_TEAM_SIZE >= 1
