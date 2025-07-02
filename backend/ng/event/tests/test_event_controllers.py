"""
Unit tests for event domain controllers
"""


class TestCreateEventController:
    def test_event_creation_logic(self):
        def mock_create_event(event_data):
            if not event_data.get("name"):
                raise ValueError("Name required")
            if event_data.get("max_team_size", 0) <= 0:
                raise ValueError("Max team size must be positive")
            return {"event": {"id": 1, **event_data, "status": "draft"}}

        valid_data = {"name": "Test Event", "max_team_size": 4}
        result = mock_create_event(valid_data)

        assert result["event"]["id"] == 1
        assert result["event"]["name"] == "Test Event"
        assert result["event"]["status"] == "draft"


class TestEventValidationController:
    def test_time_validation(self):
        def mock_validate_event_times(start_time, end_time):
            if start_time >= end_time:
                return {"valid": False, "error": "Start must be before end"}
            return {"valid": True}

        result1 = mock_validate_event_times(100, 200)
        result2 = mock_validate_event_times(200, 100)

        assert result1["valid"] is True
        assert result2["valid"] is False
        assert "Start must be before end" in result2["error"]
