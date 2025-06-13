from plugin.event_registration.models.EventRegistration import EventRegistration
from plugin.event_registration.models.Demographics import Demographics
from CTFd.models import db
from datetime import timedelta,datetime



class TestDemographicsModel:

    def test_demographics_repr(self):
        """Test the string representation of Demographics model."""
        demographics = Demographics()
        demographics.event_id = 5678
        demographics.user_id = 1234
        currtime = db.func.now()
        demographics.reg_timestamp = currtime

        repr_str = repr(demographics)
        assert "Demographics" in repr_str
        assert "id=5678" in repr_str
        assert "user_id=1234" in repr_str
        assert f"reg_timestamp={currtime}" in repr_str


class TestEventRegistrationModel:
    """Test suite for EventRegistration model."""
    
    def test_event_registration_repr(self):
        """Test the string representation of EventRegistration model."""
        registration = EventRegistration()
        registration.event_id = 1234

        repr_str = repr(registration)
        assert "Registration" in repr_str
        assert "id=1234" in repr_str

    def test_event_registration_defaults(self):
        """Test default values for EventRegistration model."""
        registration = EventRegistration()
        #Figure this out later
        assert registration.reg_open is False or registration.reg_open is None , "Default reg_open should be False"
        assert registration.public is False or registration.public is None , "Default public should be False"
        assert registration.reg_start_date is None, "Default reg_start_date should be None"
        assert registration.reg_end_date is None, "Default reg_end_date should be None"

class TestEventRegistrationConstraints:
    """Test suite for EventRegistration model constraints."""
    
    def test_event_registration_time_constraints(self):
        """Test that registration start and end dates follow the constraints."""
        from plugin.utils import validate_event_registration_creation
        curr = datetime.utcnow()
        future_start = (curr + timedelta(days=1)).isoformat()
        future_end = (curr + timedelta(days=2)).isoformat()

        # Valid case: start < end
        valid, errors = validate_event_registration_creation(
            {
                "event_id": 1234,
                "public": True,
                "reg_open": True,
                "reg_start_date": future_start,
                "reg_end_date": future_end,
            }
        )
        assert valid, f"Should be valid but got errors: {errors}"

        # Invalid case: start >= end
        valid, errors = validate_event_registration_creation(
            {
                "event_id": 1,
                "public": True,
                "reg_open": True,
                "reg_start_date": future_end,
                "reg_end_date": future_start,
            }
        )
        assert not valid, "Should be invalid due to start >= end"
    
    def test_event_reg_time_both_or_neither_constraint(self):
        """Test that both times must be provided together or neither."""
        from plugin.utils import validate_event_registration_creation

        now = datetime.utcnow()
        start = (now + timedelta(hours=1)).isoformat()
        end = (now + timedelta(days=2)).isoformat()

        valid, errors = validate_event_registration_creation({"event_id": 1234, "public": True, "reg_open": True})
        assert valid

        valid, errors = validate_event_registration_creation({"event_id": 1234, "public": True, "reg_open": True, "reg_start_date": start})
        assert not valid
        assert "reg_end_date" in errors

        valid, errors = validate_event_registration_creation({"event_id": 1234, "public": True, "reg_open": True, "reg_end_date": start})
        assert not valid
        assert "reg_start_date" in errors

        valid, errors = validate_event_registration_creation(
            {"event_id": 1234, "public": True, "reg_open": True, "reg_start_date": start, "reg_end_date": end}
        )
        print(valid,errors)
        assert valid, "Should be valid when both times are provided"
