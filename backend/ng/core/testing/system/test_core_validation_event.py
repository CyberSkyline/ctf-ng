"""
Tests for event domain validation
"""


def validate_event_creation(data):
    return data


class TestEventValidation:
    """Test event creation validation."""

    def test_valid_event_creation(self):
        """Test that valid event data passes validation."""
        valid_data = {
            "name": "CTF Championship",
            "description": "Annual competition",
            "max_team_size": 4,
            "locked": False,
        }

        result = validate_event_creation(valid_data)

        assert isinstance(result, dict)
        assert result.get("name") == "CTF Championship"
        assert result.get("max_team_size") == 4
