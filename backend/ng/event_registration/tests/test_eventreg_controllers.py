"""
Controller tests for event registration domain
"""

from flask import g

from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.Demographic import Demographic
from ..controllers.join_event_controller import join_event_controller


def test_join_event_controller_with_new_team(app, user, open_event_reg):
    """Test the main join controller when creating a new team."""
    with app.test_request_context(json={"event_id": open_event_reg.event_id, "team_name": "The New Crew"}):
        g.user = user
        g.event = open_event_reg.event
        g.validated_data = {"team_name": "The New Crew"}
        g.json_data = {"team_name": "The New Crew"}
        g.user_eligibility = {"can_join": True}

        result_dict = join_event_controller()

        assert isinstance(result_dict, dict)
        assert "team" in result_dict
        assert "demographic" in result_dict

        team_object = result_dict["team"]
        assert isinstance(team_object, Team)
        assert team_object.name == "The New Crew"

        member = TeamMember.find_by_user_and_event(user.id, open_event_reg.event_id)
        assert member is not None
        assert member.team_id == team_object.id

        demographic = Demographic.find_by_user_and_event(user.id, open_event_reg.event_id)
        assert demographic is not None


def test_join_event_controller_with_existing_team(app, user, open_event_reg, team_factory):
    """Test the main join controller when joining an existing team."""
    existing_team = team_factory(event=open_event_reg.event)

    with app.test_request_context(
        json={
            "event_id": open_event_reg.event_id,
            "invite_code": existing_team.invite_code,
        }
    ):
        g.user = user
        g.event = open_event_reg.event
        g.team = existing_team
        g.validated_data = {"invite_code": existing_team.invite_code}
        g.json_data = {"invite_code": existing_team.invite_code}
        g.user_eligibility = {"can_join": True}

        result_dict = join_event_controller()

        assert isinstance(result_dict, dict)
        assert "team" in result_dict
        assert "team_member" in result_dict
        assert "demographic" in result_dict

        team_object = result_dict["team"]
        assert isinstance(team_object, Team)
        assert team_object.id == existing_team.id

        member = TeamMember.find_by_user_and_event(user.id, open_event_reg.event_id)
        assert member is not None
        assert member.team_id == team_object.id

        demographic = Demographic.find_by_user_and_event(user.id, open_event_reg.event_id)
        assert demographic is not None
