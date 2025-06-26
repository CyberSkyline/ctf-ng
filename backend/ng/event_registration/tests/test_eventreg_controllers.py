import pytest
import time
from ..controllers.join_event_existing_team import join_event_existing_team
from ..controllers.join_event_new_team import join_event_new_team
from tests.helpers import gen_user as gen_user_original


class DBWrapper:
    def __init__(self, session):
        self.session = session

def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


pytestmark = pytest.mark.db

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
