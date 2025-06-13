"""
/plugin/tests/integration/team/test_team_controllers.py
Tests team controller business logic
"""

import time
import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.team.controllers.create_team import create_team
from plugin.team.controllers.join_team import join_team
from plugin.team.controllers.leave_team import leave_team
from plugin.team.controllers.get_team_info import get_team_info
from plugin.team.controllers.list_teams_in_event import list_teams_in_event
from plugin.team.controllers.remove_member import remove_member
from plugin.team.controllers.transfer_captaincy import transfer_captaincy
from plugin.team.controllers.update_team import update_team
from plugin.team.controllers.disband_team import disband_team
from plugin.team.models.Team import Team
from plugin.team.models.TeamMember import TeamMember
from plugin.team.models.enums import TeamRole


class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_unique_user(db_wrapper):
    """Generate a user with unique email to avoid conflicts."""
    timestamp = str(int(time.time() * 1000000))
    return gen_user_original(db_wrapper, name=f"user_{timestamp}", email=f"user_{timestamp}@example.com")


@pytest.mark.db
def test_create_team_sets_creator_as_captain(db_session, event):
    """Test that team creator becomes captain."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    result = create_team("Test Team", event.id, creator.id)

    assert result["success"]
    team = result["team"]
    captain_member = TeamMember.query.filter_by(team_id=team.id, role=TeamRole.CAPTAIN).first()
    assert captain_member.user_id == creator.id


@pytest.mark.db
def test_join_team_adds_member(db_session, event):
    """Test joining a team."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    invite_code = team_result["invite_code"]

    join_result = join_team(joiner.id, invite_code)

    assert join_result["success"]
    member = TeamMember.query.filter_by(team_id=team_result["team"].id, user_id=joiner.id).first()
    assert member.role == TeamRole.MEMBER


@pytest.mark.db
def test_leave_team_removes_member(db_session, event):
    """Test leaving a team."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    leave_result = leave_team(joiner.id, event.id)

    assert leave_result["success"]
    member = TeamMember.query.filter_by(team_id=team_result["team"].id, user_id=joiner.id).first()
    assert member is None


@pytest.mark.db
def test_captain_cannot_leave_team_with_members(db_session, event):
    """Test that captain cannot leave team with other members."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    leave_result = leave_team(creator.id, event.id)

    assert not leave_result["success"]
    assert "cannot leave" in leave_result["error"]


@pytest.mark.db
def test_transfer_captaincy(db_session, event):
    """Test transferring team captaincy."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    transfer_result = transfer_captaincy(team_result["team"].id, joiner.id, creator.id)

    assert transfer_result["success"]

    old_captain = TeamMember.query.filter_by(team_id=team_result["team"].id, user_id=creator.id).first()
    new_captain = TeamMember.query.filter_by(team_id=team_result["team"].id, user_id=joiner.id).first()
    assert old_captain.role == TeamRole.MEMBER
    assert new_captain.role == TeamRole.CAPTAIN


@pytest.mark.db
def test_remove_member_by_captain(db_session, event):
    """Test that captain can remove members."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    remove_result = remove_member(team_result["team"].id, joiner.id, creator.id, is_admin=False)

    assert remove_result["success"]
    member = TeamMember.query.filter_by(team_id=team_result["team"].id, user_id=joiner.id).first()
    assert member is None


@pytest.mark.db
def test_update_team_by_captain(db_session, event):
    """Test that captain can update team."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    team_result = create_team("Original Name", event.id, creator.id)

    update_result = update_team(team_result["team"].id, creator.id, new_name="Updated Name")

    assert update_result["success"]
    team = Team.query.get(team_result["team"].id)
    assert team.name == "Updated Name"


@pytest.mark.db
def test_disband_team_by_captain(db_session, event):
    """Test that captain can disband team."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)

    disband_result = disband_team(team_result["team"].id, creator.id, is_admin=False)

    assert disband_result["success"]
    team = Team.query.get(team_result["team"].id)
    assert team is None


@pytest.mark.db
def test_list_teams_in_event(db_session, event):
    """Test listing teams in an event."""
    db_wrapper = DBWrapper(db_session)
    creator1 = gen_unique_user(db_wrapper)
    creator2 = gen_unique_user(db_wrapper)

    create_team("Team 1", event.id, creator1.id)
    create_team("Team 2", event.id, creator2.id)

    teams_result = list_teams_in_event(event.id)

    assert teams_result["success"]
    assert len(teams_result["teams"]) == 2


@pytest.mark.db
def test_get_team_info(db_session, event):
    """Test getting team information."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    info_result = get_team_info(team_result["team"].id)

    assert info_result["success"]
    assert info_result["team"]["name"] == "Test Team"
    assert len(info_result["team_members"]) == 2


@pytest.mark.db
def test_joining_full_team_fails(db_session, event):
    """Test that joining a full team fails."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    event.max_team_size = 2
    db_session.commit()

    team_result = create_team("Small Team", event.id, creator.id)
    invite_code = team_result["invite_code"]

    joiner1 = gen_unique_user(db_wrapper)
    join_team(joiner1.id, invite_code)

    joiner2 = gen_unique_user(db_wrapper)
    join_result = join_team(joiner2.id, invite_code)

    assert not join_result["success"]
    assert "full" in join_result["error"]


@pytest.mark.db
def test_cannot_join_team_twice(db_session, event):
    """Test that user cannot join the same team twice."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    join_team(joiner.id, team_result["invite_code"])

    join_result = join_team(joiner.id, team_result["invite_code"])

    assert not join_result["success"]
    assert "already" in join_result["error"]


@pytest.mark.db
def test_cannot_join_multiple_teams_in_same_event(db_session, event):
    """Test that user cannot join multiple teams in the same event."""
    db_wrapper = DBWrapper(db_session)
    creator1 = gen_unique_user(db_wrapper)
    creator2 = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team1_result = create_team("Team 1", event.id, creator1.id)
    team2_result = create_team("Team 2", event.id, creator2.id)

    join_team(joiner.id, team1_result["invite_code"])

    join_result = join_team(joiner.id, team2_result["invite_code"])

    assert not join_result["success"]
    assert "already" in join_result["error"]


@pytest.mark.db
def test_locked_event_prevents_team_creation(db_session, event):
    """Test that teams cannot be created in locked events."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)

    event.locked = True
    db_session.commit()

    result = create_team("Test Team", event.id, creator.id)

    assert not result["success"]
    assert "locked" in result["error"]


@pytest.mark.db
def test_locked_team_prevents_joining(db_session, event):
    """Test that users cannot join locked teams."""
    db_wrapper = DBWrapper(db_session)
    creator = gen_unique_user(db_wrapper)
    joiner = gen_unique_user(db_wrapper)

    team_result = create_team("Test Team", event.id, creator.id)
    team = Team.query.get(team_result["team"].id)
    team.locked = True
    db_session.commit()

    join_result = join_team(joiner.id, team_result["invite_code"])

    assert not join_result["success"]
    assert "locked" in join_result["error"]
