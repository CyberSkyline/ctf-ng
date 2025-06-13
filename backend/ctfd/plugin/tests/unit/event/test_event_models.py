"""
/backend/ctfd/plugin/tests/unit/event/test_event_models.py
Unit tests for event model logic without database dependencies.
"""

from datetime import datetime, timedelta

from plugin.event.models.Event import Event


class TestEventModelLogic:
    """Test Event model properties and methods."""

    def test_event_repr_method(self):
        """Test the string representation of Event model."""
        event = Event()
        event.name = "CTF Challenge 2024"

        repr_str = repr(event)
        assert "Event" in repr_str
        assert "CTF Challenge 2024" in repr_str

    def test_event_locked_status_defaults(self):
        """Test that event locked status defaults correctly."""
        event = Event()
        assert event.locked is False or event.locked is None, "Event should not be locked by default"

    def test_event_max_team_size_bounds(self):
        """Test max_team_size attribute exists and can be set."""
        event = Event()
        event.max_team_size = 10
        assert event.max_team_size == 10

        # Test edge values
        event.max_team_size = 1
        assert event.max_team_size == 1

        event.max_team_size = 100
        assert event.max_team_size == 100


class TestEventTimeConstraints:
    """Test event time-related constraints and validations."""

    def test_event_time_constraint_validation(self):
        """Test that start_time < end_time constraint is understood."""
        from plugin.utils import validate_event_creation

        now = datetime.utcnow()
        future_start = (now + timedelta(hours=1)).isoformat()
        future_end = (now + timedelta(hours=2)).isoformat()

        # Valid: start < end
        valid, errors = validate_event_creation(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "start_time": future_start,
                "end_time": future_end,
            }
        )
        assert valid, f"Should be valid but got errors: {errors}"

        # Invalid: start > end
        valid, errors = validate_event_creation(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "start_time": future_end,
                "end_time": future_start,
            }
        )
        assert not valid
        assert "end_time" in errors
        assert "before" in errors["end_time"].lower()

    def test_event_time_both_or_neither_constraint(self):
        """Test that both times must be provided together or neither."""
        from plugin.utils import validate_event_creation

        now = datetime.utcnow()
        future_time = (now + timedelta(hours=1)).isoformat()

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 4})
        assert valid

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 4, "start_time": future_time})
        assert not valid
        assert "end_time" in errors

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 4, "end_time": future_time})
        assert not valid
        assert "start_time" in errors


class TestEventBusinessRules:
    """Test event-related business rule validations."""

    def test_event_name_validation_edge_cases(self):
        """Test edge cases for event name validation."""
        from plugin.utils import validate_event_creation

        valid, errors = validate_event_creation({"name": "", "max_team_size": 4})
        assert not valid
        assert "name" in errors

        valid, errors = validate_event_creation({"name": "   ", "max_team_size": 4})
        assert not valid
        assert "name" in errors

        valid, errors = validate_event_creation({"name": "イベント2024 🎯", "max_team_size": 4})
        assert valid

        from plugin import config

        if hasattr(config, "EVENT_NAME_MAX_LENGTH"):
            long_name = "A" * (config.EVENT_NAME_MAX_LENGTH + 1)
            valid, errors = validate_event_creation({"name": long_name, "max_team_size": 4})
            assert not valid
            assert "name" in errors

    def test_event_description_length_limits(self):
        """Test event description validation."""
        from plugin.utils import validate_event_creation
        from plugin import config

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 4})
        assert valid

        valid, errors = validate_event_creation(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "description": "A test event for unit testing",
            }
        )
        assert valid

        if hasattr(config, "EVENT_DESCRIPTION_MAX_LENGTH"):
            long_desc = "A" * (config.EVENT_DESCRIPTION_MAX_LENGTH + 1)
            valid, errors = validate_event_creation(
                {"name": "Test Event", "max_team_size": 4, "description": long_desc}
            )
            assert not valid
            assert "description" in errors

    def test_event_max_team_size_minimum_value(self):
        """Test that max_team_size has minimum value of 1."""
        from plugin.utils import validate_event_creation

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 1})
        assert valid

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": 0})
        assert not valid
        assert "max_team_size" in errors

        valid, errors = validate_event_creation({"name": "Test Event", "max_team_size": -1})
        assert not valid
        assert "max_team_size" in errors
