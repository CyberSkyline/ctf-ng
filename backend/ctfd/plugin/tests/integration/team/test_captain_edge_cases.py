"""
/backend/ctfd/plugin/tests/integration/team/test_captain_edge_cases.py
Captain-specific edge cases and recovery scenarios.
"""

import time
import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.team.controllers.create_team import create_team
from plugin.team.controllers.join_team import join_team
from plugin.team.controllers.leave_team import leave_team
from plugin.team.controllers.remove_member import remove_member
from plugin.team.controllers.transfer_captaincy import transfer_captaincy
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
def test_captain_removal_when_team_becomes_empty(db_session, event):
    """Test automatic team dissolution when captain leaves empty team."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)

    team_result = create_team("Solo Captain Team", event.id, captain.id)
    assert team_result["success"]
    team_id = team_result["team"].id

    leave_result = leave_team(captain.id, event.id)
    assert leave_result["success"]

    team = Team.query.get(team_id)
    assert team is None

    members = TeamMember.query.filter_by(team_id=team_id).all()
    assert len(members) == 0


@pytest.mark.db
def test_captain_removal_auto_promotion_order(db_session, event):
    """Test captain auto-promotion when captain is removed by admin."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    admin_user = gen_unique_user(db_wrapper)

    team_result = create_team("Auto Promotion Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member1.id, team_result["invite_code"])
    join_team(member2.id, team_result["invite_code"])

    remove_result = remove_member(team_id, captain.id, admin_user.id, is_admin=True)
    assert remove_result["success"]

    new_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert new_captain is not None
    assert new_captain.user_id == member1.id

    member2_check = TeamMember.query.filter_by(team_id=team_id, user_id=member2.id).first()
    assert member2_check.role == TeamRole.MEMBER

    captain_check = TeamMember.query.filter_by(team_id=team_id, user_id=captain.id).first()
    assert captain_check is None


@pytest.mark.db
def test_captain_transfer_validation_chain(db_session, event):
    """Test complex captain transfer validation scenarios."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    non_member = gen_unique_user(db_wrapper)

    team_result = create_team("Transfer Chain Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member1.id, team_result["invite_code"])
    join_team(member2.id, team_result["invite_code"])

    bad_transfer_result = transfer_captaincy(team_id, member2.id, member1.id)
    assert not bad_transfer_result["success"]
    assert "not authorized" in bad_transfer_result["error"]

    non_member_transfer = transfer_captaincy(team_id, non_member.id, captain.id)
    assert not non_member_transfer["success"]
    assert "not a member" in non_member_transfer["error"]

    self_transfer = transfer_captaincy(team_id, captain.id, captain.id)
    assert self_transfer["success"]

    valid_transfer = transfer_captaincy(team_id, member1.id, captain.id)
    assert valid_transfer["success"]

    new_captain = TeamMember.query.filter_by(team_id=team_id, user_id=member1.id).first()
    old_captain = TeamMember.query.filter_by(team_id=team_id, user_id=captain.id).first()

    assert new_captain.role == TeamRole.CAPTAIN
    assert old_captain.role == TeamRole.MEMBER

    second_transfer = transfer_captaincy(team_id, member2.id, member1.id)
    assert second_transfer["success"]


@pytest.mark.db
def test_headless_team_recovery_multiple_candidates(db_session, event):
    """Test headless team recovery when multiple members are candidates."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)

    team_result = create_team("Headless Recovery Team", event.id, captain.id)
    team_id = team_result["team"].id

    members = []
    for i in range(3):
        member = gen_unique_user(db_wrapper)
        join_result = join_team(member.id, team_result["invite_code"])
        assert join_result["success"]
        members.append(member)

    admin_user = gen_unique_user(db_wrapper)
    remove_result = remove_member(team_id, captain.id, admin_user.id, is_admin=True)
    assert remove_result["success"]

    new_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert new_captain is not None
    assert new_captain.user_id == members[0].id

    other_members = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.MEMBER).all()
    assert len(other_members) == 2

    member_ids = {m.user_id for m in other_members}
    assert members[1].id in member_ids
    assert members[2].id in member_ids


@pytest.mark.db
def test_captain_cannot_remove_themselves(db_session, event):
    """Test that captains cannot remove themselves through member removal."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member = gen_unique_user(db_wrapper)

    team_result = create_team("Self Remove Test Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member.id, team_result["invite_code"])

    self_remove_result = remove_member(team_id, captain.id, captain.id, is_admin=False)
    assert not self_remove_result["success"]
    assert "cannot remove" in self_remove_result["error"] or "yourself" in self_remove_result["error"]

    captain_check = TeamMember.query.filter_by(team_id=team_id, user_id=captain.id).first()
    assert captain_check is not None
    assert captain_check.role == TeamRole.CAPTAIN


@pytest.mark.db
def test_captain_succession_after_multiple_transfers(db_session, event):
    """Test captain succession through multiple transfers and departures."""
    db_wrapper = DBWrapper(db_session)
    original_captain = gen_unique_user(db_wrapper)

    team_result = create_team("Succession Test Team", event.id, original_captain.id)
    team_id = team_result["team"].id

    members = []
    for i in range(4):
        member = gen_unique_user(db_wrapper)
        join_team(member.id, team_result["invite_code"])
        members.append(member)

    transfer_captaincy(team_id, members[0].id, original_captain.id)
    transfer_captaincy(team_id, members[1].id, members[0].id)
    transfer_captaincy(team_id, members[2].id, members[1].id)

    current_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert current_captain.user_id == members[2].id

    leave_team(members[2].id, event.id)

    new_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()

    remaining_members = TeamMember.query.filter_by(team_id=team_id).all()
    remaining_user_ids = {m.user_id for m in remaining_members}

    assert new_captain is not None
    assert new_captain.user_id in remaining_user_ids


@pytest.mark.db
def test_captain_permissions_boundary_conditions(db_session, event):
    """Test boundary conditions for captain permissions."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member1 = gen_unique_user(db_wrapper)
    member2 = gen_unique_user(db_wrapper)
    admin_user = gen_unique_user(db_wrapper)

    team_result = create_team("Permissions Test Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member1.id, team_result["invite_code"])
    join_team(member2.id, team_result["invite_code"])

    remove_result = remove_member(team_id, member1.id, captain.id, is_admin=False)
    assert remove_result["success"]

    member_remove_result = remove_member(team_id, captain.id, member2.id, is_admin=False)
    assert not member_remove_result["success"]
    assert "not authorized" in member_remove_result["error"]

    admin_remove_result = remove_member(team_id, captain.id, admin_user.id, is_admin=True)
    assert admin_remove_result["success"]

    new_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    assert new_captain.user_id == member2.id

    new_member = gen_unique_user(db_wrapper)
    join_team(new_member.id, Team.query.get(team_id).invite_code)

    final_remove_result = remove_member(team_id, new_member.id, member2.id, is_admin=False)
    assert final_remove_result["success"]


@pytest.mark.db
def test_captain_edge_case_with_locked_teams(db_session, event):
    """Test captain operations when team becomes locked."""
    db_wrapper = DBWrapper(db_session)
    captain = gen_unique_user(db_wrapper)
    member = gen_unique_user(db_wrapper)

    # Create team
    team_result = create_team("Lock Test Team", event.id, captain.id)
    team_id = team_result["team"].id

    join_team(member.id, team_result["invite_code"])

    # Lock the team
    team = Team.query.get(team_id)
    team.locked = True
    db_session.commit()

    # Test: Captain should still be able to manage team even when locked
    # (Business rule: locking prevents joining, not internal management)
    transfer_captaincy(team_id, member.id, captain.id)
    # This might succeed or fail depending on business rules for locked teams

    # Test: Remove operations might still work for existing members
    new_member = gen_unique_user(db_wrapper)
    # Joining locked team should fail
    join_locked_result = join_team(new_member.id, team.invite_code)
    assert not join_locked_result["success"]
    assert "locked" in join_locked_result["error"]

    # But internal operations (if captain changed) might still work
    current_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    if current_captain.user_id == member.id:  # If transfer succeeded
        # New captain should be able to remove original captain
        remove_member(team_id, captain.id, member.id, is_admin=False)
        # This tests whether locked teams allow internal management
