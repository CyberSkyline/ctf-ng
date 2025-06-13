"""
/backend/ctfd/plugin/tests/integration/team/test_complex_team_operations.py
Complex team operation workflows and edge cases.
"""

import time
import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.team.controllers.create_team import create_team
from plugin.team.controllers.join_team import join_team
from plugin.team.controllers.leave_team import leave_team
from plugin.team.controllers.remove_member import remove_member
from plugin.team.controllers.transfer_captaincy import transfer_captaincy
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
def test_team_full_lifecycle_single_transaction(db_session, event):
    """Test complete team lifecycle in a single transaction."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    member3 = gen_unique_user(db_wrapper)

    team_result = create_team("Lifecycle Team", event.id, captain.id)
    assert team_result["success"]
    team_id = team_result["team"].id
    original_invite = team_result["invite_code"]

    join_result1 = join_team(member1.id, original_invite)
    join_result2 = join_team(member2.id, original_invite)
    join_result3 = join_team(member3.id, original_invite)
    assert all([join_result1["success"], join_result2["success"], join_result3["success"]])

    transfer_result = transfer_captaincy(team_id, member1.id, captain.id)
    assert transfer_result["success"]

    remove_result = remove_member(team_id, member2.id, member1.id, is_admin=False)
    assert remove_result["success"]

    team = Team.query.get(team_id)
    assert team.invite_code != original_invite

    leave_result = leave_team(captain.id, event.id)
    assert leave_result["success"]

    remaining_members = TeamMember.query.filter_by(team_id=team_id).all()
    assert len(remaining_members) == 2

    captain_member = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert captain_member.user_id == member1.id

    regular_member = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.MEMBER).first()
    assert regular_member.user_id == member3.id


@pytest.mark.db
def test_concurrent_team_creation_race_conditions(db_session, event):
    """Test handling of concurrent team creation scenarios."""
    db_wrapper = DBWrapper(db_session)

    users = [gen_unique_user(db_wrapper) for _ in range(5)]
    teams = []

    for i, user in enumerate(users):
        result = create_team(f"Race Team {i}", event.id, user.id)
        assert result["success"]
        teams.append(result)

    invite_codes = [team["invite_code"] for team in teams]
    assert len(set(invite_codes)) == len(invite_codes), "All invite codes should be unique"

    team_count = Team.query.filter_by(event_id=event.id).count()
    assert team_count == 5


@pytest.mark.db
def test_team_member_limit_enforcement_edge_cases(db_session, event):
    """Test edge cases around team member limits."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)

    event.max_team_size = 3
    db_session.commit()

    team_result = create_team("Small Team", event.id, captain.id)
    invite_code = team_result["invite_code"]

    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)

    join_result1 = join_team(member1.id, invite_code)
    join_result2 = join_team(member2.id, invite_code)
    assert join_result1["success"]
    assert join_result2["success"]

    extra_member = gen_unique_user(db_wrapper)
    overfill_result = join_team(extra_member.id, invite_code)
    assert not overfill_result["success"]
    assert "full" in overfill_result["error"]

    remove_result = remove_member(team_result["team"].id, member2.id, captain.id, is_admin=False)
    assert remove_result["success"]

    new_member = gen_unique_user(db_wrapper)
    join_result3 = join_team(new_member.id, Team.query.get(team_result["team"].id).invite_code)
    assert join_result3["success"]


@pytest.mark.db
def test_captain_edge_case_recovery_scenarios(db_session, event):
    """Test recovery from various captain edge case scenarios."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)

    team_result = create_team("Recovery Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member1.id, team_result["invite_code"])
    join_team(member2.id, team_result["invite_code"])

    self_remove_result = remove_member(team_id, captain.id, captain.id, is_admin=False)
    assert not self_remove_result["success"]

    transfer_result = transfer_captaincy(team_id, member1.id, captain.id)
    assert transfer_result["success"]

    leave_result = leave_team(captain.id, event.id)
    assert leave_result["success"]

    remove_result = remove_member(team_id, member2.id, member1.id, is_admin=False)
    assert remove_result["success"]

    final_leave_result = leave_team(member1.id, event.id)
    assert final_leave_result["success"]

    team = Team.query.get(team_id)
    assert team is None


@pytest.mark.db
def test_cross_event_team_isolation(db_session, event, event2):
    """Test that team operations are properly isolated between events."""
    db_wrapper = DBWrapper(db_session)
    user = gen_unique_user(db_wrapper)

    team1_result = create_team("Event1 Team", event.id, user.id)
    team2_result = create_team("Event2 Team", event2.id, user.id)

    assert team1_result["success"]
    assert team2_result["success"]

    member1 = TeamMember.query.filter_by(team_id=team1_result["team"].id, user_id=user.id).first()
    member2 = TeamMember.query.filter_by(team_id=team2_result["team"].id, user_id=user.id).first()

    assert member1.role == TeamRole.CAPTAIN
    assert member2.role == TeamRole.CAPTAIN

    leave_result = leave_team(user.id, event.id)
    assert leave_result["success"]

    member2_check = TeamMember.query.filter_by(team_id=team2_result["team"].id, user_id=user.id).first()
    assert member2_check is not None
    assert member2_check.role == TeamRole.CAPTAIN

    team1_check = Team.query.get(team1_result["team"].id)
    team2_check = Team.query.get(team2_result["team"].id)

    assert team1_check is None
    assert team2_check is not None


@pytest.mark.db
def test_invite_code_regeneration_workflow(db_session, event):
    """Test complete invite code regeneration workflow."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)

    team_result = create_team("Code Regen Team", event.id, captain.id)
    team_id = team_result["team"].id
    original_code = team_result["invite_code"]

    join_result1 = join_team(member1.id, original_code)
    assert join_result1["success"]

    remove_result = remove_member(team_id, member1.id, captain.id, is_admin=False)
    assert remove_result["success"]

    team = Team.query.get(team_id)
    new_code = team.invite_code
    assert new_code != original_code

    old_code_result = join_team(member2.id, original_code)
    assert not old_code_result["success"]
    assert "Invalid invite code" in old_code_result["error"]

    new_code_result = join_team(member2.id, new_code)
    assert new_code_result["success"]


@pytest.mark.db
def test_admin_override_team_operations(db_session, event):
    """Test admin override capabilities in team operations."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    admin_user = gen_unique_user(db_wrapper)

    team_result = create_team("Admin Test Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member1.id, team_result["invite_code"])

    admin_remove_result = remove_member(team_id, captain.id, admin_user.id, is_admin=True)
    assert admin_remove_result["success"]

    admin_disband_result = disband_team(team_id, admin_user.id, is_admin=True)
    assert admin_disband_result["success"]

    team = Team.query.get(team_id)
    assert team is None
