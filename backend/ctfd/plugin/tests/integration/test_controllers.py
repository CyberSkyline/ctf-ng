"""
/plugin/tests/integration/test_controllers.py
Tests controller business logic
"""

from CTFd.models import db
from tests.helpers import gen_user

from ..helpers import create_ctfd, destroy_ctfd


class TestControllers:
    def test_team_creation_with_invite_codes(self):
        """Check that team creation generates unique invite codes."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            assert world_result["success"]
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            result = TeamController.create_team("Test Team", world_id, creator.id)

            assert result["success"]
            assert result["team"].name == "Test Team"
            assert result["invite_code"] is not None
            assert len(result["invite_code"]) == 8

        destroy_ctfd(app)

    def test_joining_full_team_fails(self):
        """Check that joining a full team gets rejected."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            team_result = TeamController.create_team("Small Team", world_id, creator.id, limit=2)
            team_id = team_result["team"].id

            user1 = gen_user(db, name="user1", email="user1@test.com")
            user2 = gen_user(db, name="user2", email="user2@test.com")

            join1 = TeamController.join_team(user1.id, team_id, world_id)
            assert join1["success"]

            join2 = TeamController.join_team(user2.id, team_id, world_id)
            assert not join2["success"]
            assert "full" in join2["error"].lower()

        destroy_ctfd(app)

    def test_invite_code_joining(self):
        """Check that users can join teams using invite codes."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            team_result = TeamController.create_team("Secret Team", world_id, creator.id)
            invite_code = team_result["invite_code"]

            user = gen_user(db, name="user1", email="user1@test.com")
            result = TeamController.join_team_by_invite_code(user.id, invite_code)

            assert result["success"]
            assert result["joined_via_invite"]
            assert result["invite_code"] == invite_code
            assert result["team"].name == "Secret Team"

        destroy_ctfd(app)

    def test_world_default_team_size(self):
        """Check that teams use world default size when not specified."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Custom World", default_team_size=6)
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            team_result = TeamController.create_team("Auto Team", world_id, creator.id)

            assert team_result["success"]
            assert team_result["team"].limit == 6

        destroy_ctfd(app)

    def test_manual_captain_assignment(self):
        """Check that captains can be assigned and removed manually."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            team_result = TeamController.create_team("Leadership Team", world_id, creator.id)
            team_id = team_result["team"].id

            user1 = gen_user(db, name="user1", email="user1@test.com")
            user2 = gen_user(db, name="user2", email="user2@test.com")

            join1 = TeamController.join_team(user1.id, team_id, world_id)
            join2 = TeamController.join_team(user2.id, team_id, world_id)

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

        destroy_ctfd(app)

    def test_auto_captain_assignment(self):
        """Check that team creator automatically becomes captain."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")

            team_result = TeamController.create_team("Auto Team", world_id, creator.id)
            team_id = team_result["team"].id

            captain_result = TeamController.get_team_captain(team_id)
            assert captain_result["success"]
            assert captain_result["has_captain"]
            assert captain_result["captain_id"] == creator.id

            user2 = gen_user(db, name="user2", email="user2@test.com")
            join2 = TeamController.join_team(user2.id, team_id, world_id)
            assert join2["success"]

            captain_result = TeamController.get_team_captain(team_id)
            assert captain_result["success"]
            assert captain_result["has_captain"]
            assert captain_result["captain_id"] == creator.id

        destroy_ctfd(app)

    def test_government_training_scenario(self):
        """Check that users can be in different teams across worlds."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController
            from ...controllers.user_controller import UserController

            user = gen_user(db, name="agent", email="agent@gov.test")

            basic_world = WorldController.create_world("Basic Security Training")
            advanced_world = WorldController.create_world("Advanced Threat Response")

            basic_world_id = basic_world["world"].id
            advanced_world_id = advanced_world["world"].id

            red_creator = gen_user(db, name="red_leader", email="red@gov.test")
            blue_creator = gen_user(db, name="blue_leader", email="blue@gov.test")

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

        destroy_ctfd(app)

    def test_update_team_captain_only(self):
        """Check that only captain or admin can update team."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            captain = gen_user(db, name="captain", email="captain@test.com")
            team_result = TeamController.create_team("Original Name", world_id, captain.id)
            team_id = team_result["team"].id

            member = gen_user(db, name="member", email="member@test.com")
            join_result = TeamController.join_team(member.id, team_id, world_id)
            assert join_result["success"]

            update_result = TeamController.update_team(team_id, member.id, new_name="Hacked Name")
            assert not update_result["success"]
            assert "not authorized" in update_result["error"].lower()

            update_result = TeamController.update_team(team_id, captain.id, new_name="New Name")
            assert update_result["success"]
            assert update_result["team"].name == "New Name"

        destroy_ctfd(app)

    def test_disband_team_captain_only(self):
        """Check that only captain or admin can disband team."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            captain = gen_user(db, name="captain", email="captain@test.com")
            team_result = TeamController.create_team("Doomed Team", world_id, captain.id)
            team_id = team_result["team"].id

            member = gen_user(db, name="member", email="member@test.com")
            join_result = TeamController.join_team(member.id, team_id, world_id)
            assert join_result["success"]

            disband_result = TeamController.disband_team(team_id, member.id)
            assert not disband_result["success"]
            assert "not authorized" in disband_result["error"].lower()

            disband_result = TeamController.disband_team(team_id, captain.id)
            assert disband_result["success"]
            assert "disbanded" in disband_result["message"]

            from ...models.Team import Team

            team = Team.query.get(team_id)
            assert team is None

        destroy_ctfd(app)

    def test_remove_member_captain_only(self):
        """Check that only captain or admin can remove team members."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController
            from ...models.TeamMember import TeamMember
            from CTFd.models import db

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            captain = gen_user(db, name="captain", email="captain@test.com")
            team_result = TeamController.create_team("Exclusive Team", world_id, captain.id)
            team_id = team_result["team"].id

            member1 = gen_user(db, name="member1", email="member1@test.com")
            member2 = gen_user(db, name="member2", email="member2@test.com")

            join1 = TeamController.join_team(member1.id, team_id, world_id)
            assert join1["success"]

            join2 = TeamController.join_team(member2.id, team_id, world_id)
            assert join2["success"]

            db.session.expire_all()

            remove_result = TeamController.remove_member(team_id, member2.id, member1.id)
            assert not remove_result["success"]
            assert "not authorized" in remove_result["error"].lower()

            db.session.expire_all()

            remove_result = TeamController.remove_member(team_id, member2.id, captain.id)
            assert remove_result["success"]
            assert "removed successfully" in remove_result["message"]

            membership = TeamMember.query.filter_by(user_id=member2.id, team_id=team_id).first()
            assert membership is None

            db.session.expire_all()

            remove_result = TeamController.remove_member(team_id, captain.id, captain.id)
            assert not remove_result["success"]
            assert "cannot remove themselves" in remove_result["error"].lower()

        destroy_ctfd(app)

    def test_creator_already_in_team(self):
        """Check that creator cannot create team if already in a team in that world."""
        app = create_ctfd()

        with app.app_context():
            from ...controllers.team_controller import TeamController
            from ...controllers.world_controller import WorldController

            world_result = WorldController.create_world("Test World")
            world_id = world_result["world"].id

            creator = gen_user(db, name="creator", email="creator@test.com")
            team1_result = TeamController.create_team("First Team", world_id, creator.id)
            assert team1_result["success"]

            team2_result = TeamController.create_team("Second Team", world_id, creator.id)
            assert not team2_result["success"]
            assert "already in a team" in team2_result["error"]

        destroy_ctfd(app)
