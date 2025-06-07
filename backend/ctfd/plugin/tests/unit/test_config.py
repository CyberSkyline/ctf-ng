"""
plugin/tests/unit/test_config.py
Sanity checks for the plugin's config values
"""

from ...config import DEFAULT_TEAM_SIZE, MAX_TEAM_SIZE, INVITE_CODE_GENERATION_ATTEMPTS


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
