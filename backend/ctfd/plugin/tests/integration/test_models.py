"""
/plugin/tests/integration/test_models.py
Tests database models
"""

import pytest
from plugin.world.models.World import World
from plugin.team.models.Team import Team
from plugin.user.models.User import User
from plugin.team.models.TeamMember import TeamMember
from tests.helpers import gen_user
from CTFd.models import db as _db


@pytest.mark.db
class TestModels:
    def test_create_world(self, db_session):
        """Check that worlds can be created."""
        world = World(name="Test World", description="Test")
        db_session.add(world)
        db_session.commit()

        assert world.id is not None
        assert world.name == "Test World"

    def test_create_team(self, db_session, world):
        """Check that teams can be created in a world."""
        team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
        db_session.add(team)
        db_session.commit()

        assert team.id is not None
        assert team.name == "Test Team"
        assert team.world_id == world.id

    def test_create_user(self, db_session):
        """Check that plugin users can be created."""
        ctfd_user = gen_user(_db, name="testuser", email="test@example.com")

        ng_user = User(id=ctfd_user.id)
        db_session.add(ng_user)
        db_session.commit()

        assert ng_user.id == ctfd_user.id

    def test_team_membership(self, db_session, world):
        """Check that users can join teams."""
        ctfd_user = gen_user(_db, name="testuser", email="test@example.com")
        ng_user = User(id=ctfd_user.id)
        db_session.add(ng_user)
        team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
        db_session.add(team)
        db_session.commit()
        membership = TeamMember(user_id=ctfd_user.id, team_id=team.id, world_id=world.id)
        db_session.add(membership)
        db_session.commit()

        assert membership.user_id == ctfd_user.id
        assert membership.team_id == team.id
        assert membership.world_id == world.id
