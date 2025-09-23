import pytest
# from unittest.mock import patch
# from sqlalchemy.exc import IntegrityError

from ...core.exceptions import ValidationError
from datetime import datetime
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
# from ...user.models.User import User
# from ...event.models.Event import Event

class Test_Create_Team:
    def test_should_create_team(self, event):
        team = Team.create_team(
            name="Test Team",
            event_id=event.id,
        )

        refreshed_team = Team.query.get(team.id)
        assert refreshed_team is not None
        assert refreshed_team.name == "Test Team"
        assert refreshed_team.event_id == event.id
        assert refreshed_team.invite_code is not None
        assert refreshed_team.ranked is True

    def test_should_error_if_validation_fails(self, event):
        with pytest.raises(ValidationError):
            Team.create_team(
                name="",
                event_id=event.id,
            )

    # def test_should_not_commit_team_if_set_to_false(self, event, db_session):
    #     with patch.object(db_session, 'commit') as mock_commit:
    #         Team.create_team(
    #             name="Test Team",
    #             event_id=event.id,
    #             commit=False,
    #         )
    #         mock_commit.assert_not_called()

class Test_Create_Team_With_Captain:
    def test_should_create_team_with_captain(self, event, user):
        team = Team.create_team_with_captain(
            name="Test Team with Captain",
            event_id=event.id,
            captain_id=user.id,
        )

        refreshed_team = Team.query.get(team.id)
        assert refreshed_team is not None
        assert refreshed_team.name == "Test Team with Captain"

        team_member = TeamMember.find_by_user_and_team(user.id, team.id)
        assert team_member is not None
        assert team_member.role == TeamRole.CAPTAIN

    def test_should_error_if_captain_is_already_on_team(self, event, user):
        Team.create_team_with_captain(
            name="Test Team with Captain",
            event_id=event.id,
            captain_id=user.id,
        )

        with pytest.raises(ValidationError):
            team2 = Team.create_team_with_captain(
                name="Test Team with Existing Captain",
                event_id=event.id,
                captain_id=user.id,
            )

            assert team2 is None

class Test_Update_Invite_Code:
    def test_should_choose_unique_invite_code(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])
        old_code = team.invite_code

        team.update_invite_code()

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.invite_code == team.invite_code
        assert refreshed_team.invite_code != old_code

    def test_should_update_specified_invite_code(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])
        old_code = team.invite_code
        new_code = Team.get_unique_invite_code()

        team.update_invite_code(new_code=new_code)

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.invite_code == new_code
        assert refreshed_team.invite_code != old_code

    # def test_should_respect_commit_flag(self, event, team_factory, db_session):
    #     team = team_factory(event=event)

    #     with patch.object(db_session, 'commit') as mock_commit:
    #         team.update_invite_code(commit=False)
    #         mock_commit.assert_not_called()

    #     with patch.object(db_session, 'commit') as mock_commit:
    #         team.update_invite_code(commit=True)
    #         mock_commit.assert_called_once()

class Test_Update_Name:
    def test_should_update_team_name(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])
        old_name = team.name
        new_name = "Updated Team Name"

        team.update_team(name=new_name)

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.name == new_name
        assert refreshed_team.name != old_name

    # def test_should_respect_commit_flag(self, event, team_factory, db_session):
    #     team = team_factory(event=event)
    #     new_name = "Updated Team Name"

    #     with patch.object(db_session, 'commit') as mock_commit:
    #         team.update_name(new_name, commit=False)
    #         mock_commit.assert_not_called()

    #     with patch.object(db_session, 'commit') as mock_commit:
    #         team.update_name(new_name, commit=True)
    #         mock_commit.assert_called_once()

class Test_Find_By_Id:
    def test_should_find_team_by_id(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])

        found_team = Team.find_by_id(team.id)

        assert found_team is not None
        assert found_team.id == team.id

    def test_should_return_none_if_team_not_found(self, db_session):
        found_team = Team.find_by_id(9999)  # Assuming this ID does not exist
        assert found_team is None


class Test_Find_By_Invite_Code:
    def test_should_find_team_by_invite_code(self, event, team_factory,user):
        team = team_factory(event=event, members=[user])

        found_team = Team.find_by_invite_code(team.invite_code)

        assert found_team is not None
        assert found_team.id == team.id

    def test_should_return_none_if_invite_code_not_found(self, db_session):
        found_team = Team.find_by_invite_code("nonexistentcode")
        assert found_team is None

class Test_Team_Name_Contains_Member_Name:
    def test_should_return_true_if_name_contains_member_name(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])
        team.name = f"{user.name} Team"

        assert Team.team_name_contains_member_name(team.name, [user.name]) is True

    def test_should_return_false_if_name_does_not_contain_member_name(self, event, team_factory, user):
        team = team_factory(event=event, members=[user])
        team.name = "Some Other Team Name"

        assert Team.team_name_contains_member_name(team.name, [user.name]) is False

    def test_name_checks(self,event, team_factory, user_factory):
        user = user_factory(name="Alex John Smith")
        team = team_factory(event=event, members=[user])
        team.name = "Alex Smith"

        assert Team.team_name_contains_member_name(team.name, [user.ctfd_user.name]) is True

    def test_more_name_checks(self, event, team_factory, user_factory):
        user1 = user_factory(name="Alex Ng")
        team1 = team_factory(event=event, members=[user1])
        team1.name = "pwning"

        assert Team.team_name_contains_member_name(team1.name, [user1.ctfd_user.name]) is False

        team1.name = "pwni ng"

        assert Team.team_name_contains_member_name(team1.name, [user1.ctfd_user.name]) is True


    def test_even_more_name_checks(self, event, team_factory, user_factory):
        user = user_factory(name="A Smith")
        team = team_factory(event=event, members=[user])
        team.name = "a hacker"

        assert Team.team_name_contains_member_name(team.name, [user.ctfd_user.name]) is False

#Partial matches like this fail using the current logic, but adjusting the logic to allow for partial matches
#Would cause false positives such as "Alex Ng" "pwning"
"""
    def test_partial_match(self, event, team_factory, user_factory):
        user = user_factory(name="Jonathan Doe")
        team = team_factory(event=event, members=[user])
        team.name = "Jon Squad"

        assert Team.team_name_contains_member_name(team.name, [user.ctfd_user.name]) is True
"""


class Test_TeamMember_Validation:

    def test_validates_max_team_size_constraint(self, event_factory, team_factory, user_factory):
        """
        Test that adding a member to a full team raises ValidationError
        """
        # Create event with max team size of 2
        event = event_factory(max_team_size=2)

        # Create full team with 2 members
        user1 = user_factory(name="User 1", email="user1@test.com")
        user2 = user_factory(name="User 2", email="user2@test.com")
        team = team_factory(event=event, members=[user1, user2])

        # Try to add a third member
        user3 = user_factory(name="User 3", email="user3@test.com")

        with pytest.raises(ValidationError) as exc_info:
            TeamMember.validate({
                "user_id": user3.id,
                "team_id": team.id,
                "event_id": event.id,
                "role": TeamRole.MEMBER
            })

        assert "is full (2/2)" in str(exc_info.value)

    def test_allows_adding_member_when_team_not_full(self, event_factory, team_factory, user_factory):
        """
        Test that adding a member to a non full team succeeds
        """
        # Create event with max team size of 4
        event = event_factory(max_team_size=4)

        # Create team with 2 members
        user1 = user_factory(name="User 1", email="user1@test.com")
        user2 = user_factory(name="User 2", email="user2@test.com")
        team = team_factory(event=event, members=[user1, user2])

        # Try to add a third member
        user3 = user_factory(name="User 3", email="user3@test.com")

        # This should not raise an exception
        validated_data = TeamMember.validate({
            "user_id": user3.id,
            "team_id": team.id,
            "event_id": event.id,
            "role": TeamRole.MEMBER
        })

        assert validated_data["user_id"] == user3.id
        assert validated_data["team_id"] == team.id

class Test_Setting_Team_End_Time:
    def test_should_set_end_time(self, team_factory, user):
        team = team_factory(members=[user])
        assert team.end_time is None

        team.set_end_time(end_time=datetime(2024, 12, 31, 23, 59, 59))

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.end_time is not None
        assert str(refreshed_team.end_time) == "2024-12-31 23:59:59"

