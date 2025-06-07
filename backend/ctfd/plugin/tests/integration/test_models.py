"""
/plugin/tests/integration/test_models.py
Tests database models
"""

from CTFd.models import db
from tests.helpers import gen_user

from ..helpers import create_ctfd, destroy_ctfd, get_models


class TestModels:
    def test_create_world(self):
        """Check that worlds can be created."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]

            world = World(name="Test World", description="Test")
            db.session.add(world)
            db.session.commit()

            assert world.id is not None
            assert world.name == "Test World"

        destroy_ctfd(app)

    def test_create_team(self):
        """Check that teams can be created in a world."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]

            world = World(name="Test World")
            db.session.add(world)
            db.session.commit()

            team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
            db.session.add(team)
            db.session.commit()

            assert team.id is not None
            assert team.name == "Test Team"
            assert team.world_id == world.id

        destroy_ctfd(app)

    def test_create_user(self):
        """Check that plugin users can be created."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            User = models["User"]

            ctfd_user = gen_user(db, name="testuser", email="test@example.com")

            ng_user = User(id=ctfd_user.id)
            db.session.add(ng_user)
            db.session.commit()

            assert ng_user.id == ctfd_user.id

        destroy_ctfd(app)

    def test_team_membership(self):
        """Check that users can join teams."""
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

            team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
            db.session.add(team)
            db.session.commit()

            membership = TeamMember(user_id=ctfd_user.id, team_id=team.id, world_id=world.id)
            db.session.add(membership)
            db.session.commit()

            assert membership.user_id == ctfd_user.id
            assert membership.team_id == team.id
            assert membership.world_id == world.id

        destroy_ctfd(app)
