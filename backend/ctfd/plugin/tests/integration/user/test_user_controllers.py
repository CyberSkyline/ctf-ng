"""
/plugin/tests/integration/user/test_user_controllers.py
Tests user controller business logic
"""

import time
import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.team.controllers.create_team import create_team
from plugin.user.controllers.get_user_teams import get_user_teams


class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


@pytest.mark.db
def test_get_user_teams_across_events(db_session, event, event2):
    """Test getting user teams across multiple events."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    create_team("Team 1", event.id, creator.id)
    create_team("Team 2", event2.id, creator.id)

    teams_result = get_user_teams(creator.id)

    assert teams_result["success"]
    assert len(teams_result["teams"]) == 2
