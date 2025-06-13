"""
/plugin/tests/integration/event/test_event_controllers.py
Tests event controller business logic
"""

import pytest
from datetime import datetime
from plugin.event.controllers.create_event import create_event


@pytest.mark.db
def test_create_event_with_all_fields(db_session):
    """Test creating an event with all optional fields."""
    start_time = datetime(2025, 6, 1, 10, 0, 0)
    end_time = datetime(2025, 6, 1, 18, 0, 0)

    result = create_event(
        name="Full Event",
        description="Complete event with all fields",
        max_team_size=5,
        start_time=start_time,
        end_time=end_time,
        locked=False,
    )

    assert result["success"]
    assert result["event"]["name"] == "Full Event"
    assert result["event"]["max_team_size"] == 5
    assert result["event"]["locked"] is False
