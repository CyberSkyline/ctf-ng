"""
/plugin/tests/integration/test_constraints.py
Tests database constraints
"""

import pytest
from CTFd.models import db
from tests.helpers import gen_user
from sqlalchemy.exc import IntegrityError

from ..helpers import create_ctfd, destroy_ctfd, get_models


class TestConstraints:

    def test_unique_user_world_constraint(self):
        """Check that users can only be in one team per world."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]
            User = models["User"]
            TeamMember = models["TeamMember"]

            ctfd_user = gen_user(db, name="testuser", email="test@example.com")

            world = World(name="Test World")
            db.session.add(world)
            db.session.commit()

            ng_user = User(id=ctfd_user.id)
            db.session.add(ng_user)

            team1 = Team(name="Team 1", world_id=world.id, limit=4, invite_code="TEAM1ABC")
            team2 = Team(name="Team 2", world_id=world.id, limit=4, invite_code="TEAM2DEF")
            db.session.add_all([team1, team2])
            db.session.commit()

            membership1 = TeamMember(user_id=ctfd_user.id, team_id=team1.id, world_id=world.id)
            db.session.add(membership1)
            db.session.commit()

            membership2 = TeamMember(user_id=ctfd_user.id, team_id=team2.id, world_id=world.id)
            db.session.add(membership2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

        destroy_ctfd(app)

    def test_team_member_count_property(self):
        """Check that team member count property works correctly."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]
            User = models["User"]
            TeamMember = models["TeamMember"]

            world = World(name="Test World")
            db.session.add(world)
            db.session.commit()

            team = Team(name="Test Team", world_id=world.id, limit=3, invite_code="TESTTEAM")
            db.session.add(team)
            db.session.commit()

            assert team.member_count == 0
            assert team.is_full == False

            user1 = gen_user(db, name="user1", email="user1@example.com")
            user2 = gen_user(db, name="user2", email="user2@example.com")

            ng_user1 = User(id=user1.id)
            ng_user2 = User(id=user2.id)
            db.session.add_all([ng_user1, ng_user2])

            membership1 = TeamMember(user_id=user1.id, team_id=team.id, world_id=world.id)
            membership2 = TeamMember(user_id=user2.id, team_id=team.id, world_id=world.id)
            db.session.add_all([membership1, membership2])
            db.session.commit()

            assert team.member_count == 2
            assert team.is_full == False

        destroy_ctfd(app)

    def test_unique_invite_codes(self):
        """Check that invite codes must be unique."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]

            world = World(name="Test World")
            db.session.add(world)
            db.session.commit()

            team1 = Team(name="Team 1", world_id=world.id, limit=4, invite_code="SAMECODE")
            db.session.add(team1)
            db.session.commit()

            team2 = Team(name="Team 2", world_id=world.id, limit=4, invite_code="SAMECODE")
            db.session.add(team2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

        destroy_ctfd(app)
