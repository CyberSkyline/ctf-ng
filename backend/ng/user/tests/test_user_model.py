"""
Tests for the User model
"""

import pytest
from unittest.mock import patch

from ..models.User import User


class TestUser:
    """
    Test the User model string representation
    """
    def test_repr(self, user_factory):
        """
        Test the string representation of the model
        """
        ng_user = user_factory(name = "Test User", email = "test@example.com")
        expected = f"<NgUser id={ng_user.id}>"
        assert repr(ng_user) == expected

    def test_create_user_with_commit(self, db_session, user):
        """
        Test creating a user extension with commit
        """
        with patch.object(db_session, "commit") as mock_commit:
            ng_user = User.create_user(user_id = user.id, commit = True)
            mock_commit.assert_called_once()

        assert ng_user.id == user.id
        assert ng_user in db_session

    def test_create_user_without_commit(self, db_session, user):
        """
        Test creating a user extension without commit
        """
        with patch.object(db_session, "commit") as mock_commit:
            ng_user = User.create_user(user_id = user.id, commit = False)
            mock_commit.assert_not_called()

        assert ng_user.id == user.id
        assert ng_user in db_session

    def test_create_user_returns_instance(self, db_session, user):
        """
        Test that create_user returns the User instance
        """
        existing_ng_user = User.query.get(user.id)
        if existing_ng_user:
            db_session.delete(existing_ng_user)
            db_session.commit()

        ng_user = User.create_user(user_id = user.id)

        assert isinstance(ng_user, User)
        assert ng_user.id == user.id

    def test_find_by_id_existing(self, user_factory):
        """
        Test finding an existing user by ID
        """
        ng_user = user_factory(name = "Find Me", email = "findme@example.com")

        found_user = User.find_by_id(ng_user.id)

        assert found_user is not None
        assert found_user.id == ng_user.id
        assert found_user.ctfd_user.name == "Find Me"

    def test_find_by_id_nonexistent(self, db_session):
        """
        Test finding a non existent user returns None
        """
        found_user = User.find_by_id(99999)

        assert found_user is None

    def test_find_or_create_by_ctfd_id_existing(self, user_factory):
        """
        Test find_or_create when user already exists
        """
        ng_user = user_factory(name = "Existing User", email = "existing@example.com")

        found_user = User.find_or_create_by_ctfd_id(ng_user.id)

        assert found_user.id == ng_user.id
        assert found_user.ctfd_user.name == "Existing User"

    def test_find_or_create_by_ctfd_id_creates_new(self, db_session, user):
        """
        Test find_or_create creates new user extension when none exists
        """
        existing_ng_user = User.query.get(user.id)
        if existing_ng_user:
            db_session.delete(existing_ng_user)
            db_session.commit()

        found_user = User.find_or_create_by_ctfd_id(user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.ctfd_user.name == user.name

    def test_find_or_create_commit_flag(self, db_session, user):
        """
        Test find_or_create respects commit flag when creating
        """
        existing_ng_user = User.query.get(user.id)
        if existing_ng_user:
            db_session.delete(existing_ng_user)
            db_session.commit()

        with patch.object(db_session, "commit") as mock_commit:
            User.find_or_create_by_ctfd_id(user.id, commit = False)
            mock_commit.assert_not_called()

    def test_get_all_users(self, user_factory):
        """
        Test getting all users
        """
        user1 = user_factory(name = "User 1", email = "user1@example.com")
        user2 = user_factory(name = "User 2", email = "user2@example.com")

        all_users = User.get_all_users()

        assert len(all_users) >= 2
        user_ids = [u.id for u in all_users]
        assert user1.id in user_ids
        assert user2.id in user_ids

    def test_serialize_basic(self, user_factory):
        """
        Test basic serialization without admin fields
        """
        ng_user = user_factory(name = "Serialize Me", email = "serialize@example.com")
        data = ng_user.serialize(include_admin_fields = False)

        assert data["id"] == ng_user.id
        assert data["name"] == "Serialize Me"
        assert data["email"] == "serialize@example.com"
        assert "registered_at" in data
        assert data["registered_at"].endswith("Z")
        assert "roles" not in data

    def test_serialize_with_admin_fields(self, user_factory):
        """
        Test serialization with admin fields
        """
        ng_user = user_factory(
            name = "Admin Serialize",
            email = "admin_serialize@example.com"
        )

        data = ng_user.serialize(include_admin_fields = True)

        assert data["id"] == ng_user.id
        assert data["name"] == "Admin Serialize"
        assert data["email"] == "admin_serialize@example.com"
        assert "registered_at" in data
        assert "roles" in data
        assert isinstance(data["roles"], list)

    def test_serialize_missing_ctfd_user(self):
        """
        Test serialization when ctfd_user relationship is missing
        """
        ng_user = User(id = 99999)
        data = ng_user.serialize()

        assert data["id"] == 99999
        assert "Data Inconsistency" in data["name"]
        assert data["email"] == ""
        assert data["role"] == "unknown"
        assert data["registered_at"] == ""

    def test_get_events(self, user_factory, event_factory, team_factory):
        """
        Test getting events the user is registered in
        """
        ng_user = user_factory(name = "Event User", email = "events@example.com")
        event1 = event_factory(name = "User Event 1")
        event2 = event_factory(name = "User Event 2")
        team_factory(event = event1, members = [ng_user])
        team_factory(event = event2, members = [ng_user])

        events = ng_user.get_events()

        assert len(events) == 2
        event_names = {event.name for event in events}
        assert "User Event 1" in event_names
        assert "User Event 2" in event_names

    def test_get_events_no_teams(self, user_factory):
        """
        Test getting events when user has no teams
        """
        ng_user = user_factory(name = "No Team User", email = "noteams@example.com")

        events = ng_user.get_events()

        assert len(events) == 0

    def test_get_teams(self, user_factory, event_factory, team_factory):
        """
        Test getting teams the user is a member of
        """
        ng_user = user_factory(name = "Team User", email = "teams@example.com")
        event1 = event_factory(name = "Team Event 1")
        event2 = event_factory(name = "Team Event 2")
        team_factory(event = event1, name = "Team N", members = [ng_user])
        team_factory(event = event2, name = "Team NG", members = [ng_user])

        teams = ng_user.get_teams()

        assert len(teams) == 2
        team_names = {team.name for team in teams}
        assert "Team N" in team_names
        assert "Team NG" in team_names

    def test_check_can_join_team_in_event_true(self, user_factory, event_factory):
        """
        Test user can join team when not already in event
        """
        ng_user = user_factory(name = "Available User", email = "available@example.com")
        event = event_factory(name = "Available Event")

        can_join = User.check_can_join_team_in_event(ng_user.id, event.id)

        assert can_join is True

    def test_check_can_join_team_in_event_false(
        self,
        user_factory,
        event_factory,
        team_factory
    ):
        """
        Test user cannot join team when already in event
        """
        ng_user = user_factory(name = "Busy User", email = "busy@example.com")
        event = event_factory(name = "Busy Event")
        team_factory(event = event, members = [ng_user])

        can_join = User.check_can_join_team_in_event(ng_user.id, event.id)

        assert can_join is False

    def test_get_permissions(self, user_factory):
        """
        Test getting user permissions from roles
        """
        ng_user = user_factory(name = "Permission User", email = "perms@example.com")

        permissions = ng_user.get_permissions()

        assert isinstance(permissions, list)

    def test_update_user_fields(self, db_session, user_factory):
        """
        Test updating user fields through CTFd user
        """
        ng_user = user_factory(name = "Original Name", email = "original@example.com")

        ng_user.update(name = "Updated Name", email = "updated@example.com")

        db_session.refresh(ng_user.ctfd_user)
        assert ng_user.ctfd_user.name == "Updated Name"
        assert ng_user.ctfd_user.email == "updated@example.com"

    def test_update_invalid_field_ignored(self, user_factory):
        """
        Test updating invalid field is safely ignored
        """
        ng_user = user_factory(name = "Safe User", email = "safe@example.com")
        original_name = ng_user.ctfd_user.name

        ng_user.update(invalid_field = "should_be_ignored")

        assert ng_user.ctfd_user.name == original_name

    def test_delete_user(self, user_factory):
        """
        Test deleting a single user
        """
        ng_user = user_factory(name = "Delete Me", email = "delete@example.com")
        user_id = ng_user.id

        ng_user.delete()

        found_user = User.query.get(user_id)
        assert found_user is None

    def test_delete_all_users(self, user_factory):
        """
        Test deleting all users
        """
        user_factory(name = "Delete All 1", email = "deleteall1@example.com")
        user_factory(name = "Delete All 2", email = "deleteall2@example.com")

        initial_count = User.query.count()
        assert initial_count >= 2

        User.delete_all()

        final_count = User.query.count()
        assert final_count == 0

    def test_ctfd_user_relationship(self, user_factory):
        """
        Test the ctfd_user relationship works correctly
        """
        ng_user = user_factory(
            name = "Relationship Test",
            email = "relationship@example.com"
        )

        assert ng_user.ctfd_user is not None
        assert ng_user.ctfd_user.name == "Relationship Test"
        assert ng_user.ctfd_user.email == "relationship@example.com"

    def test_team_members_relationship(self, user_factory, event_factory, team_factory):
        """
        Test the team_members relationship
        """
        ng_user = user_factory(name = "Team Member", email = "teammember@example.com")
        event = event_factory(name = "Relationship Event")
        team = team_factory(event = event, members = [ng_user])

        assert len(ng_user.team_members) == 1
        assert ng_user.team_members[0].team_id == team.id
        assert ng_user.team_members[0].event_id == event.id

    def test_team_membership_persists_after_user_update(
        self,
        user_factory,
        event_factory,
        team_factory,
        db_session
    ):
        """
        Test that user updates don't break team relationships
        """
        ng_user = user_factory(name = "Original")
        event = event_factory()
        team = team_factory(event = event, members = [ng_user])

        ng_user.update(name = "Updated Name")
        db_session.refresh(ng_user)

        teams = ng_user.get_teams()
        assert len(teams) == 1
        assert teams[0].id == team.id

    def test_failed_update_doesnt_persist(self, user_factory, db_session):
        """
        Test that failed operations don't leave partial changes
        """
        ng_user = user_factory(name = "Original")
        original_name = ng_user.ctfd_user.name

        with patch.object(db_session, 'commit', side_effect = Exception("DB Error")):
            try:
                ng_user.update(name = "Should Not Persist")
            except Exception:
                pass

        db_session.refresh(ng_user.ctfd_user)
        assert ng_user.ctfd_user.name == original_name

    # TODO
    # def test_validate_returns_data_unchanged(self):
    # ...Add more when validation is added in model
