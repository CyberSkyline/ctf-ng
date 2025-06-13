import pytest
import time
from datetime import datetime
from plugin.event_registration.controllers.join_event_existing_team import join_event_existing_team
from plugin.event_registration.controllers.join_event_new_team import join_event_new_team
from plugin.event_registration.models.EventRegistration import EventRegistration
from plugin.event_registration.controllers.create_event_registration import create_event_registration
from plugin.event.controllers.create_event import create_event
from plugin.team.controllers.create_team import create_team
from tests.helpers import gen_user as gen_user_original


class DBWrapper:
    def __init__(self, session):
        self.session = session

def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")

@pytest.mark.db
def test_join_event_with_new_team(db_session,event, event_registration):
    """Test joining an event by creating a new team."""

    user = gen_unique_user(DBWrapper(db_session))


    result = join_event_new_team(
        user_id=user.id,
        event_id=event.id,
        team_name="New Team",
    )

    assert result["success"]

@pytest.mark.db
def test_join_event_with_existing_team(db_session, event, normal_user, team_with_members, event_registration):
    """Test joining an event with an existing team."""


    result = join_event_existing_team(
        user_id=normal_user.id,
        event_id=event.id,
        invite_code=team_with_members["team"].invite_code,
    )
    assert result["success"]



@pytest.mark.db
def test_join_closed_event_fails(db_session, event, closed_event_registration, normal_user):
    """Test that joining a closed event fails."""
    
    result = join_event_new_team(
        user_id=normal_user.id,
        event_id=event.id,
        team_name="New Team",
    )

    assert not result["success"]
    assert "Event registration is not open." in result["error"]


@pytest.mark.db
def test_join_event_past_registration_period_fails(db_session, event, past_event_registration, normal_user):
    """Test that joining an event after the registration period fails."""

    result = join_event_new_team(
        user_id=normal_user.id,
        event_id=event.id,
        team_name="New Team",
    )

    assert not result["success"]
    assert "Event registration has ended." in result["error"]

@pytest.mark.db
def test_join_event_before_registration_starts_fails(db_session, event, future_event_registration, normal_user):
    """Test that joining an event before the registration starts fails."""
    

    result = join_event_new_team(
        user_id=normal_user.id,
        event_id=event.id,
        team_name="New Team",
    )

    assert not result["success"]
    assert "Event registration has not started yet." in result["error"]
    