import pytest
from unittest.mock import patch
# from sqlalchemy.exc import IntegrityError

from ...core.exceptions import ValidationError

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

    def test_should_not_commit_team_if_set_to_false(self, event):
        team = Team.create_team(
            name="Test Team",
            event_id=event.id,
            commit=False,
        )

        refreshed_team = Team.query.get(team.id)
        assert refreshed_team is None

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

        # with pytest.raises(ValidationError):
        #     Team.create_team_with_captain(
        #         name="Test Team with Existing Captain",
        #         event_id=event.id,
        #         captain_id=user.id,
        #     )
    

class Test_Update_Invite_Code:
    def test_should_choose_unique_invite_code(self, event, team_factory):
        team = team_factory(event=event)
        old_code = team.invite_code

        team.update_invite_code()

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.invite_code == team.invite_code
        assert refreshed_team.invite_code != old_code

    def test_should_update_specified_invite_code(self, event, team_factory):
        team = team_factory(event=event)
        old_code = team.invite_code
        new_code = Team.get_unique_invite_code()

        team.update_invite_code(new_code=new_code)

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.invite_code == new_code
        assert refreshed_team.invite_code != old_code

    def test_should_respect_commit_flag(self, event, team_factory, db_session):
        team = team_factory(event=event)

        with patch.object(db_session, 'commit') as mock_commit:
            team.update_invite_code(commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, 'commit') as mock_commit:
            team.update_invite_code(commit=True)
            mock_commit.assert_called_once()

class Test_Update_Name:
    def test_should_update_team_name(self, event, team_factory):
        team = team_factory(event=event)
        old_name = team.name
        new_name = "Updated Team Name"

        team.update_name(new_name)

        refreshed_team = Team.query.get(team.id)

        assert refreshed_team.name == new_name
        assert refreshed_team.name != old_name

    def test_should_respect_commit_flag(self, event, team_factory, db_session):
        team = team_factory(event=event)
        new_name = "Updated Team Name"

        with patch.object(db_session, 'commit') as mock_commit:
            team.update_name(new_name, commit=False)
            mock_commit.assert_not_called()

        with patch.object(db_session, 'commit') as mock_commit:
            team.update_name(new_name, commit=True)
            mock_commit.assert_called_once()

class Test_Find_By_Id:
    def test_should_find_team_by_id(self, event, team_factory):
        team = team_factory(event=event)

        found_team = Team.find_by_id(team.id)

        assert found_team is not None
        assert found_team.id == team.id

    def test_should_return_none_if_team_not_found(self, db_session):
        found_team = Team.find_by_id(9999)  # Assuming this ID does not exist
        assert found_team is None
        db_session.close()

class Test_Find_By_Invite_Code:
    def test_should_find_team_by_invite_code(self, event, team_factory):
        team = team_factory(event=event)

        found_team = Team.find_by_invite_code(team.invite_code)

        assert found_team is not None
        assert found_team.id == team.id

    def test_should_return_none_if_invite_code_not_found(self, db_session):
        found_team = Team.find_by_invite_code("nonexistentcode")
        assert found_team is None
        db_session.close()