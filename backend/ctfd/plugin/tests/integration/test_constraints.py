"""
/plugin/tests/integration/test_constraints.py
Tests database constraints
"""

import pytest
from tests.helpers import gen_user
from sqlalchemy.exc import IntegrityError
from plugin.team.models.Team import Team
from plugin.user.models.User import User
from plugin.team.models.TeamMember import TeamMember
from CTFd.models import db as _db


@pytest.mark.db
class TestConstraints:
    def test_unique_user_world_constraint(self, db_session, world):
        """Check that users can only be in one team per world."""
        ctfd_user = gen_user(_db, name="testuser", email="test@example.com")

        ng_user = User(id=ctfd_user.id)
        db_session.add(ng_user)

        team1 = Team(name="Team 1", world_id=world.id, limit=4, invite_code="TEAM1ABC")
        team2 = Team(name="Team 2", world_id=world.id, limit=4, invite_code="TEAM2DEF")
        db_session.add_all([team1, team2])
        db_session.commit()

        membership1 = TeamMember(user_id=ctfd_user.id, team_id=team1.id, world_id=world.id)
        db_session.add(membership1)
        db_session.commit()

        membership2 = TeamMember(user_id=ctfd_user.id, team_id=team2.id, world_id=world.id)
        db_session.add(membership2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_team_member_count_property(self, db_session, world):
        """Check that team member count property works correctly."""
        team = Team(name="Test Team", world_id=world.id, limit=3, invite_code="TESTTEAM")
        db_session.add(team)
        db_session.commit()

        assert team.member_count == 0
        assert not team.is_full

        user1 = gen_user(_db, name="user1", email="user1@example.com")
        user2 = gen_user(_db, name="user2", email="user2@example.com")

        ng_user1 = User(id=user1.id)
        ng_user2 = User(id=user2.id)
        db_session.add_all([ng_user1, ng_user2])

        membership1 = TeamMember(user_id=user1.id, team_id=team.id, world_id=world.id)
        membership2 = TeamMember(user_id=user2.id, team_id=team.id, world_id=world.id)
        db_session.add_all([membership1, membership2])
        db_session.commit()

        db_session.refresh(team)

        assert team.member_count == 2
        assert not team.is_full

        user3 = gen_user(_db, name="user3", email="user3@example.com")
        ng_user3 = User(id=user3.id)
        db_session.add(ng_user3)

        membership3 = TeamMember(user_id=user3.id, team_id=team.id, world_id=world.id)
        db_session.add(membership3)
        db_session.commit()

        db_session.refresh(team)

        assert team.member_count == 3
        assert team.is_full

    def test_unique_invite_codes(self, db_session, world):
        """Check that invite codes must be unique."""
        team1 = Team(name="Team 1", world_id=world.id, limit=4, invite_code="SAMECODE")
        db_session.add(team1)
        db_session.commit()

        team2 = Team(name="Team 2", world_id=world.id, limit=4, invite_code="SAMECODE")
        db_session.add(team2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()
