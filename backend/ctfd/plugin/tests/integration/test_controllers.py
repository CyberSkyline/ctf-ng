"""
/plugin/tests/integration/test_controllers.py
Tests controller business logic
"""

import pytest
from tests.helpers import gen_user as gen_user_original
from plugin.controllers.team_controller import TeamController
from plugin.controllers.world_controller import WorldController
from plugin.controllers.user_controller import UserController
from plugin.models.Team import Team
from plugin.models.TeamMember import TeamMember


# Wrapper to adapt db_session for gen_user
class DBWrapper:
    def __init__(self, session):
        self.session = session


def gen_user(db_session, **kwargs):
    """Wrapper function to adapt db_session for gen_user."""
    db_wrapper = DBWrapper(db_session)
    return gen_user_original(db_wrapper, **kwargs)


@pytest.mark.db
class TestControllers:
    def test_team_creation_with_invite_codes(self, db_session, world):
        """Check that team creation generates unique invite codes."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")
        result = TeamController.create_team("Test Team", world.id, creator.id)

        assert result["success"]
        assert result["team"].name == "Test Team"
        assert result["invite_code"] is not None
        assert len(result["invite_code"]) == 8

    def test_joining_full_team_fails(self, db_session, world):
        """Check that joining a full team gets rejected."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")
        team_result = TeamController.create_team("Small Team", world.id, creator.id, limit=2)
        team_id = team_result["team"].id

        user1 = gen_user(db_session, name="user1", email="user1@test.com")
        user2 = gen_user(db_session, name="user2", email="user2@test.com")

        join1 = TeamController.join_team(user1.id, team_id, world.id)
        assert join1["success"]

        join2 = TeamController.join_team(user2.id, team_id, world.id)
        assert not join2["success"]
        assert "full" in join2["error"].lower()

    def test_invite_code_joining(self, db_session, world):
        """Check that users can join teams using invite codes."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")
        team_result = TeamController.create_team("Secret Team", world.id, creator.id)
        invite_code = team_result["invite_code"]

        user = gen_user(db_session, name="user1", email="user1@test.com")
        result = TeamController.join_team_by_invite_code(user.id, invite_code)

        assert result["success"]
        assert result["joined_via_invite"]
        assert result["invite_code"] == invite_code
        assert result["team"].name == "Secret Team"

    def test_world_default_team_size(self, db_session):
        """Check that teams use world default size when not specified."""
        world_result = WorldController.create_world("Custom World", default_team_size=6)
        world_id = world_result["world"]["id"]

        creator = gen_user(db_session, name="creator", email="creator@test.com")
        team_result = TeamController.create_team("Auto Team", world_id, creator.id)

        assert team_result["success"]
        assert team_result["team"].limit == 6

    def test_manual_captain_assignment(self, db_session, world):
        """Check that captains can be assigned and removed manually."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")
        team_result = TeamController.create_team("Leadership Team", world.id, creator.id)
        team_id = team_result["team"].id

        user1 = gen_user(db_session, name="user1", email="user1@test.com")
        user2 = gen_user(db_session, name="user2", email="user2@test.com")

        join1 = TeamController.join_team(user1.id, team_id, world.id)
        join2 = TeamController.join_team(user2.id, team_id, world.id)

        assert join1["success"]
        assert join2["success"]

        assign_result = TeamController.transfer_captaincy(team_id, user2.id, creator.id)
        assert assign_result["success"]

        captain_result = TeamController.get_team_captain(team_id)
        assert captain_result["success"]
        assert captain_result["has_captain"]
        assert captain_result["captain_id"] == user2.id

        remove_result = TeamController.remove_captain(team_id)
        assert remove_result["success"]

        captain_check = TeamController.get_team_captain(team_id)
        assert captain_check["success"]
        assert not captain_check["has_captain"]

    def test_auto_captain_assignment(self, db_session, world):
        """Check that team creator automatically becomes captain."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")

        team_result = TeamController.create_team("Auto Team", world.id, creator.id)
        team_id = team_result["team"].id

        captain_result = TeamController.get_team_captain(team_id)
        assert captain_result["success"]
        assert captain_result["has_captain"]
        assert captain_result["captain_id"] == creator.id

        user2 = gen_user(db_session, name="user2", email="user2@test.com")
        join2 = TeamController.join_team(user2.id, team_id, world.id)
        assert join2["success"]

        captain_result = TeamController.get_team_captain(team_id)
        assert captain_result["success"]
        assert captain_result["has_captain"]
        assert captain_result["captain_id"] == creator.id

    def test_government_training_scenario(self, db_session):
        """Check that users can be in different teams across worlds."""
        user = gen_user(db_session, name="agent", email="agent@gov.test")

        basic_world = WorldController.create_world("Basic Security Training")
        advanced_world = WorldController.create_world("Advanced Threat Response")

        basic_world_id = basic_world["world"]["id"]
        advanced_world_id = advanced_world["world"]["id"]

        red_creator = gen_user(db_session, name="red_leader", email="red@gov.test")
        blue_creator = gen_user(db_session, name="blue_leader", email="blue@gov.test")

        red_team = TeamController.create_team("Red Team", basic_world_id, red_creator.id)
        blue_team = TeamController.create_team("Blue Team", advanced_world_id, blue_creator.id)

        join_red = TeamController.join_team(user.id, red_team["team"].id, basic_world_id)
        join_blue = TeamController.join_team(user.id, blue_team["team"].id, advanced_world_id)

        assert join_red["success"]
        assert join_blue["success"]

        user_teams = UserController.get_user_teams(user.id)
        assert user_teams["success"]
        assert len(user_teams["teams"]) == 2

        world_names = [team["world_name"] for team in user_teams["teams"]]
        assert "Basic Security Training" in world_names
        assert "Advanced Threat Response" in world_names

    def test_update_team_captain_only(self, db_session, world):
        """Check that only captain or admin can update team."""
        captain = gen_user(db_session, name="captain", email="captain@test.com")
        team_result = TeamController.create_team("Original Name", world.id, captain.id)
        team_id = team_result["team"].id

        member = gen_user(db_session, name="member", email="member@test.com")
        join_result = TeamController.join_team(member.id, team_id, world.id)
        assert join_result["success"]

        update_result = TeamController.update_team(team_id, member.id, new_name="Hacked Name")
        assert not update_result["success"]
        assert "not authorized" in update_result["error"].lower()

        update_result = TeamController.update_team(team_id, captain.id, new_name="New Name")
        assert update_result["success"]
        assert update_result["team"].name == "New Name"

    def test_disband_team_captain_only(self, db_session, world):
        """Check that only captain or admin can disband team."""
        captain = gen_user(db_session, name="captain", email="captain@test.com")
        team_result = TeamController.create_team("Doomed Team", world.id, captain.id)
        team_id = team_result["team"].id

        member = gen_user(db_session, name="member", email="member@test.com")
        join_result = TeamController.join_team(member.id, team_id, world.id)
        assert join_result["success"]

        disband_result = TeamController.disband_team(team_id, member.id)
        assert not disband_result["success"]
        assert "not authorized" in disband_result["error"].lower()

        disband_result = TeamController.disband_team(team_id, captain.id)
        assert disband_result["success"]
        assert "disbanded" in disband_result["message"]

        team = Team.query.get(team_id)
        assert team is None

    def test_remove_member_captain_only(self, db_session, world):
        """Check that only captain or admin can remove team members."""
        captain = gen_user(db_session, name="captain", email="captain@test.com")
        team_result = TeamController.create_team("Exclusive Team", world.id, captain.id)
        team_id = team_result["team"].id

        member1 = gen_user(db_session, name="member1", email="member1@test.com")
        member2 = gen_user(db_session, name="member2", email="member2@test.com")

        join1 = TeamController.join_team(member1.id, team_id, world.id)
        assert join1["success"]

        join2 = TeamController.join_team(member2.id, team_id, world.id)
        assert join2["success"]

        db_session.expire_all()

        remove_result = TeamController.remove_member(team_id, member2.id, member1.id)
        assert not remove_result["success"]
        assert "not authorized" in remove_result["error"].lower()

        db_session.expire_all()

        remove_result = TeamController.remove_member(team_id, member2.id, captain.id)
        assert remove_result["success"]
        assert "removed successfully" in remove_result["message"]

        membership = TeamMember.query.filter_by(user_id=member2.id, team_id=team_id).first()
        assert membership is None

        db_session.expire_all()

        remove_result = TeamController.remove_member(team_id, captain.id, captain.id)
        assert not remove_result["success"]
        assert "cannot remove themselves" in remove_result["error"].lower()

    def test_creator_already_in_team(self, db_session, world):
        """Check that creator cannot create team if already in a team in that world."""
        creator = gen_user(db_session, name="creator", email="creator@test.com")
        team1_result = TeamController.create_team("First Team", world.id, creator.id)
        assert team1_result["success"]

        team2_result = TeamController.create_team("Second Team", world.id, creator.id)
        assert not team2_result["success"]
        assert "already in a team" in team2_result["error"]
