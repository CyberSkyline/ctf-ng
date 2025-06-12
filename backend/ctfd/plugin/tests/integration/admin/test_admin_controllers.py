"""
/plugin/tests/integration/admin/test_admin_controllers.py
Tests admin controller business logic
"""

import time
import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.team.controllers.create_team import create_team
from plugin.admin.controllers.get_data_counts import get_data_counts
from plugin.admin.controllers.cleanup_headless_teams import cleanup_headless_teams


class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


@pytest.mark.db
def test_get_data_counts(db_session, event):
    """Test getting basic data counts."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    create_team("Test Team", event.id, creator.id)

    counts = get_data_counts()

    assert counts["events"] >= 1
    assert counts["teams"] >= 1
    assert counts["users"] >= 1
    assert counts["team_members"] >= 1


@pytest.mark.db
def test_cleanup_headless_teams(db_session, event):
    """Test cleaning up teams without captains."""
    result = cleanup_headless_teams()

    assert result["success"]
    assert "Fixed 0 headless teams" in result["message"]
