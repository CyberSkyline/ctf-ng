"""
Model tests for event registration domain
"""

import pytest
from datetime import datetime, timedelta
from ...core.exceptions import ValidationError
from ..models.Demographic import Demographic
from ..models.EventRegistration import EventRegistration
from ...core.validation.event_registration import validate_event_registration_creation


class TestEventRegistrationModel:
    """Test suite for the EventRegistration SQLAlchemy model."""

    def test_repr(self, open_event_reg):
        """Test the string representation of the model."""
        assert f"event_id={open_event_reg.event_id}" in repr(open_event_reg)

    def test_defaults(self):
        """Test the default values for a new instance."""
        reg = EventRegistration()
        assert reg.public is None
        assert reg.reg_open is None
        assert reg.reg_start_date is None
        assert reg.reg_end_date is None


class TestDemographicModel:
    """Test suite for the Demographic SQLAlchemy model."""

    def test_repr(self, user, event):
        """Test the string representation of the model."""
        demo = Demographic(user_id=user.id, event_id=event.id)
        assert f"user_id={user.id}" in repr(demo)
        assert f"event_id={event.id}" in repr(demo)


class TestEventRegistrationValidation:
    """Test suite for the event registration validation functions."""

    def test_validation_success(self, event):
        """Test a successful validation with all fields."""
        data = {
            "event_id": event.id,
            "public": True,
            "reg_open": True,
            "reg_start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "reg_end_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        }

        parsed_data = validate_event_registration_creation(data)
        assert parsed_data["event_id"] == event.id

    def test_validation_invalid_date_order(self, event):
        """Test that start_date must be before end_date."""
        data = {
            "event_id": event.id,
            "reg_start_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "reg_end_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        }
        with pytest.raises(ValidationError) as e:
            validate_event_registration_creation(data)
        assert "reg_end_date" in e.value.errors
        assert "must be after" in e.value.errors["reg_end_date"]

    def test_validation_date_missing_pair(self, event):
        """Test that if one date is provided, the other must be too."""
        data = {
            "event_id": event.id,
            "reg_start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        }
        with pytest.raises(ValidationError) as e:
            validate_event_registration_creation(data)
        assert "time_constraint" in e.value.errors
