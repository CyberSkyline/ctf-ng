"""
Validation tests for event creation and registration eligibility
"""

from datetime import timedelta

import pytest

from ... import config
from ...core.exceptions import BusinessLogicError, ValidationError
from ...core.utils import utc_now
from ..models.Event import Event


class TestEventTimeConstraints:
    """Test event time-related constraints and validations."""

    def test_event_time_constraint_validation(self):
        """Test that start_time < end_time constraint is understood."""

        now = utc_now()
        future_start = (now + timedelta(hours=1)).isoformat()
        future_end = (now + timedelta(hours=2)).isoformat()

        result = Event.validate(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "start_time": future_start,
                "end_time": future_end,
            }
        )
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            Event.validate(
                {
                    "name": "Test Event",
                    "max_team_size": 4,
                    "start_time": future_end,
                    "end_time": future_start,
                }
            )
        assert "end_time" in exc_info.value.errors
        assert "after" in exc_info.value.errors["end_time"].lower()

    def test_event_time_both_or_neither_constraint(self):
        """Test that both times must be provided together or neither."""

        now = utc_now()
        future_time = (now + timedelta(hours=1)).isoformat()

        result = Event.validate({"name": "Test Event", "max_team_size": 4})
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "Test Event", "max_team_size": 4, "start_time": future_time})
        assert "time_constraint" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "Test Event", "max_team_size": 4, "end_time": future_time})
        assert "time_constraint" in exc_info.value.errors


class TestEventBusinessRules:
    """Test event-related business rule validations."""

    def test_event_name_validation_edge_cases(self):
        """Test edge cases for event name validation."""

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "", "max_team_size": 4})
        assert "name" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "   ", "max_team_size": 4})
        assert "name" in exc_info.value.errors

        result = Event.validate({"name": "イベント2024 🎯", "max_team_size": 4})
        assert result is not None

        if hasattr(config, "EVENT_NAME_MAX_LENGTH"):
            long_name = "A" * (config.EVENT_NAME_MAX_LENGTH + 1)
            with pytest.raises(ValidationError) as exc_info:
                Event.validate({"name": long_name, "max_team_size": 4})
            assert "name" in exc_info.value.errors

    def test_event_description_length_limits(self):
        """Test event description validation."""

        result = Event.validate({"name": "Test Event", "max_team_size": 4})
        assert result is not None

        result = Event.validate(
            {
                "name": "Test Event",
                "max_team_size": 4,
                "description": "A test event for unit testing",
            }
        )
        assert result is not None

        if hasattr(config, "EVENT_DESCRIPTION_MAX_LENGTH"):
            long_desc = "A" * (config.EVENT_DESCRIPTION_MAX_LENGTH + 1)
            with pytest.raises(ValidationError) as exc_info:
                Event.validate({"name": "Test Event", "max_team_size": 4, "description": long_desc})
            assert "description" in exc_info.value.errors

    def test_event_max_team_size_minimum_value(self):
        """Test that max_team_size has minimum value of 1."""

        result = Event.validate({"name": "Test Event", "max_team_size": 1})
        assert result is not None

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "Test Event", "max_team_size": 0})
        assert "max_team_size" in exc_info.value.errors

        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "Test Event", "max_team_size": -1})
        assert "max_team_size" in exc_info.value.errors


class TestEventValidationEdgeCases:
    """Test comprehensive event validation edge cases and scenarios."""

    def test_event_name_special_characters(self):
        """Test event name validation with special characters and edge cases."""
        # Valid special characters
        valid_names = [
            "Event 2024",
            "Event-2024",
            "Event_2024",
            "Event.2024",
            "Event (CTF)",
            "Event [Beta]",
            "Event @ School",
            "Event #1",
            "Multi-Word Event Name",
        ]

        for name in valid_names:
            result = Event.validate({"name": name, "max_team_size": 4})
            assert result is not None, f"Valid name '{name}' should pass validation"

        # Edge case: only whitespace variations
        invalid_names = ["   ", "\t\t\t", "\n\n\n", "", "   \t   \n   "]

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                Event.validate({"name": name, "max_team_size": 4})
            assert "name" in exc_info.value.errors, f"Invalid name '{repr(name)}' should fail validation"

    def test_event_description_special_cases(self):
        """Test event description validation edge cases."""
        # Empty string vs None
        result = Event.validate({"name": "Test Event", "max_team_size": 4, "description": ""})
        assert result is not None

        # Only whitespace
        result = Event.validate({"name": "Test Event", "max_team_size": 4, "description": "   \t   "})
        assert result is not None

        # Multiline description
        multiline_desc = """This is a test event
        with multiple lines
        and various formatting.
        It includes:
        - Line breaks
        - Special characters !@#$%
        - Unicode: 🎯 イベント"""

        result = Event.validate({"name": "Test Event", "max_team_size": 4, "description": multiline_desc})
        assert result is not None

    def test_team_size_boundary_values(self):
        """Test team size validation at boundary values."""
        # Test minimum valid value
        result = Event.validate({"name": "Test Event", "max_team_size": 1})
        assert result is not None

        # Test various valid sizes (within config limit)
        valid_sizes = [1, 2, 3, 4, 5]
        for size in valid_sizes:
            result = Event.validate({"name": f"Test Event {size}", "max_team_size": size})
            assert result is not None, f"Team size {size} should be valid"

        # Test maximum team size
        result = Event.validate({"name": "Max Size Event", "max_team_size": config.MAX_TEAM_SIZE})
        assert result is not None

        # Test exceeding maximum
        with pytest.raises(ValidationError) as exc_info:
            Event.validate({"name": "Over Max Event", "max_team_size": config.MAX_TEAM_SIZE + 1})
        assert "max_team_size" in exc_info.value.errors

        # Test invalid values
        invalid_sizes = [0, -1, -10, -999]
        for size in invalid_sizes:
            with pytest.raises(ValidationError) as exc_info:
                Event.validate({"name": f"Invalid {size}", "max_team_size": size})
            assert "max_team_size" in exc_info.value.errors

    def test_datetime_edge_cases(self):
        """Test datetime validation edge cases."""
        now = utc_now()

        # Very close times (1 second apart)
        start_time = (now + timedelta(hours=1)).isoformat()
        end_time = (now + timedelta(hours=1, seconds=1)).isoformat()

        result = Event.validate(
            {
                "name": "Close Times Event",
                "max_team_size": 4,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        assert result is not None

        # Exactly same times (should fail)
        same_time = (now + timedelta(hours=1)).isoformat()
        with pytest.raises(ValidationError) as exc_info:
            Event.validate(
                {
                    "name": "Same Times Event",
                    "max_team_size": 4,
                    "start_time": same_time,
                    "end_time": same_time,
                }
            )
        assert "end_time" in exc_info.value.errors

        # Long duration event
        long_end = (now + timedelta(days=365)).isoformat()
        result = Event.validate(
            {
                "name": "Long Event",
                "max_team_size": 4,
                "start_time": start_time,
                "end_time": long_end,
            }
        )
        assert result is not None

    def test_boolean_field_variations(self):
        """Test locked field with various boolean representations."""
        # Explicit boolean values
        result = Event.validate({"name": "Locked Event", "max_team_size": 4, "locked": True})
        assert result is not None
        assert result["locked"] is True

        result = Event.validate({"name": "Unlocked Event", "max_team_size": 4, "locked": False})
        assert result is not None
        assert result["locked"] is False

        # Default value when omitted
        result = Event.validate({"name": "Default Lock Event", "max_team_size": 4})
        assert result is not None
        # Should have default value (typically False)

    def test_comprehensive_validation_combinations(self):
        """Test various field combinations and their validation."""
        now = utc_now()
        future_start = (now + timedelta(hours=2)).isoformat()
        future_end = (now + timedelta(hours=4)).isoformat()

        # All fields provided
        result = Event.validate(
            {
                "name": "Complete Event",
                "description": "A complete event with all fields",
                "max_team_size": 8,
                "start_time": future_start,
                "end_time": future_end,
                "locked": True,
            }
        )
        assert result is not None
        assert result["name"] == "Complete Event"
        assert result["description"] == "A complete event with all fields"
        assert result["max_team_size"] == 8
        assert result["locked"] is True

        # Minimal valid event
        result = Event.validate({"name": "Minimal Event", "max_team_size": 1})
        assert result is not None
        assert result["name"] == "Minimal Event"
        assert result["max_team_size"] == 1


class TestEventAdvancedDatetimeValidation:
    """Test advanced datetime validation scenarios."""

    def test_timezone_handling(self):
        """Test datetime validation with timezone considerations."""
        now = utc_now()

        # Test with explicit timezone info (should be handled gracefully)
        future_start_tz = now + timedelta(hours=1)
        future_end_tz = now + timedelta(hours=3)

        # Convert to ISO format (framework should handle timezone)
        result = Event.validate(
            {
                "name": "Timezone Event",
                "max_team_size": 4,
                "start_time": future_start_tz.isoformat(),
                "end_time": future_end_tz.isoformat(),
            }
        )
        assert result is not None


class TestEventRegistrationEligibility:
    """Test the registration window rules enforced by Event.check_eligibility."""

    @pytest.mark.parametrize("event_kwargs,expected_error", [
        ({"registration_open": False}, "Event registration is closed."),
        (
            {"registration_start_date": timedelta(days=1), "registration_end_date": timedelta(days=2)},
            "Event registration has not started yet.",
        ),
        (
            {"registration_start_date": timedelta(days=-2), "registration_end_date": timedelta(days=-1)},
            "Event registration has ended.",
        ),
    ])
    def test_registration_blocked_outside_window(self, event_factory, user_factory, event_kwargs, expected_error):
        """Registration is rejected when closed, not yet open, or already over."""
        now = utc_now()
        event = event_factory(**{
            key: now + value if isinstance(value, timedelta) else value
            for key, value in event_kwargs.items()
        })
        user = user_factory()

        with pytest.raises(BusinessLogicError, match=expected_error):
            event.check_eligibility(user)

    def test_registration_allowed_inside_window(self, event_factory, user_factory):
        """Registration is allowed while it is open and inside its window."""
        now = utc_now()
        event = event_factory(
            registration_open=True,
            registration_start_date=now - timedelta(days=1),
            registration_end_date=now + timedelta(days=1),
        )
        user = user_factory()

        assert event.check_eligibility(user) is True
