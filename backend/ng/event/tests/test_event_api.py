"""
Test Event API
"""

import os
import base64
import pytest
from datetime import datetime, timedelta
from ...core.utils import utc_now

from ...core.utils import utc_now
from ...user.models.User import User
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...event.models.Demographic import Demographic
from ...challenge.models.Challenge import Challenge


pytestmark = pytest.mark.db


class Test_Public_Event_Listing:
    endpoint = "/ng/events"

    def test_list_public_events(self, logged_in_client, event_factory):
        event1 = event_factory(name = "Public Event 1", public = True)
        event2 = event_factory(name = "Public Event 2", public = True)

        response = logged_in_client.get(self.endpoint)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0] == event1.serialize()
        assert data["data"][1] == event2.serialize()

    def test_list_no_private_events(self, logged_in_client, event_factory):
        event2 = event_factory(name = "Private Event 2", public = True)

        response = logged_in_client.get(self.endpoint)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0] == event2.serialize()


class Test_Public_Event_Detail:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}"

    def test_get_event_details(self, logged_in_client, event_factory):
        event = event_factory(name = "Event for Detail Test", public = True)

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert data["data"] == event.serialize()

    def test_get_nonexistent_event(self, logged_in_client):
        response = logged_in_client.get(self.get_endpoint(9999))

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_private_event(self, logged_in_client, event_factory):
        event = event_factory(
            name = "Private Event for Detail Test",
            public = False
        )

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False


class Test_Event_Eligibility:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/eligibility"

    def test_check_event_eligibility(self, logged_in_client, event_factory):
        event = event_factory(name = "Eligible Event", public = True)

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] is True

    def test_check_nonexistent_event_eligibility(self, logged_in_client):
        response = logged_in_client.get(self.get_endpoint(9999))

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_check_event_eligibility_not_open(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(
            name = "Closed Event",
            public = True,
            registration_open = False
        )

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration is closed." in data["errors"][
            "business_logic"]

    def test_check_event_eligibility_before_start(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(
            name = "Event Before Start",
            public = True,
            registration_start_date = datetime.utcnow() + timedelta(days = 1),
            registration_end_date = datetime.utcnow() + timedelta(days = 2),
        )

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has not started yet." in data["errors"][
            "business_logic"]

    def test_check_event_eligibility_after_end(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(
            name = "Event After End",
            public = True,
            registration_end_date = datetime.utcnow() - timedelta(days = 1),
            registration_start_date = datetime.utcnow() - timedelta(days = 2),
        )

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has ended." in data["errors"][
            "business_logic"]

    def test_check_event_eligibility_already_registered(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory
    ):
        event = event_factory(name = "Already Registered Event", public = True)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/me/register",
            json = {
                "team_name": "Test Team",
            },
        )

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "User is already registered for this event." in data["errors"][
            "business_logic"]


class Test_Event_Registration:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/register"

    def test_register_for_event_with_new_team(
        self,
        logged_in_client,
        user,
        event_factory
    ):
        event = event_factory(name = "Event for Registration", public = True)

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Test Team",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        team = Team.query.filter_by(
            name = "Test Team",
            event_id = event.id
        ).first()
        assert data["data"] == team.serialize()

        team_member = TeamMember.query.filter_by(
            user_id = user.id,
            team_id = team.id
        ).first()
        assert team_member is not None

    def test_register_for_event_with_existing_team(
        self,
        logged_in_client,
        user_factory,
        event_factory,
        team_factory
    ):
        event = event_factory(
            name = "Event for Existing Team Registration",
            public = True
        )
        user = user_factory(name = "testuser", email = "testuser@example.com")
        existing_team = team_factory(event = event, members = [user])

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "invite_code": existing_team.invite_code,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        team = Team.query.filter_by(id = existing_team.id).first()
        assert data["data"] == team.serialize()

        team_member = TeamMember.query.filter_by(
            user_id = user.id,
            team_id = team.id
        ).first()
        assert team_member is not None

    def test_register_member_name_cannot_be_in_team_name(
        self,
        logged_in_client,
        user,
        event_factory
    ):
        event = event_factory(
            name = "Event for Invalid Team Name",
            public = True
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": user.name,
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Team name cannot include a member's name." in data["errors"][
            "validation"]

    def test_register_for_nonexistent_event(self, logged_in_client):
        response = logged_in_client.post(
            self.get_endpoint(9999),
            json = {
                "team_name": "Test Team",
            },
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_register_without_team_name_or_invite_code(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(
            name = "Event for Missing Team Info",
            public = True
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data

    def test_register_closed_event(self, logged_in_client, event_factory):
        event = event_factory(
            name = "Closed Event",
            public = True,
            registration_open = False
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Test Team",
            },
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration is closed." in data["errors"][
            "business_logic"]

    def test_register_private_event(self, logged_in_client, event_factory):
        event = event_factory(
            name = "Private Event for Registration",
            public = False
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Test Team",
            },
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_register_event_before_start(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(
            name = "Event Before Start",
            public = True,
            registration_start_date = datetime.utcnow() + timedelta(days = 1),
            registration_end_date = datetime.utcnow() + timedelta(days = 2),
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Test Team",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has not started yet." in data["errors"][
            "business_logic"]

    def test_register_event_after_end(self, logged_in_client, event_factory):
        event = event_factory(
            name = "Event After End",
            public = True,
            registration_end_date = datetime.utcnow() - timedelta(days = 1),
            registration_start_date = datetime.utcnow() - timedelta(days = 2),
        )

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Test Team",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has ended." in data["errors"][
            "business_logic"]

    def test_register_twice_for_event(
        self,
        logged_in_client,
        user,
        event_factory
    ):
        event = event_factory(
            name = "Event for Duplicate Registration",
            public = True
        )

        # First registration
        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "First Team",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        # Second registration attempt
        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json = {
                "team_name": "Second Team",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "User is already registered for this event." in data["errors"][
            "business_logic"]


class Test_Event_Team_Lookup:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/team"

    def test_get_team_for_event(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory
    ):
        event = event_factory(name = "Event for Team Lookup", public = True)
        team = team_factory(event = event, members = [user])

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == team.serialize()

    def test_get_team_for_nonexistent_event(self, logged_in_client):
        response = logged_in_client.get(self.get_endpoint(9999))

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False


class Test_Event_TeamMember_Lookup:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/team/members"

    def test_get_team_member_for_event(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory
    ):
        event = event_factory(
            name = "Event for Team Member Lookup",
            public = True
        )
        team = team_factory(event = event, members = [user])

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == [member.serialize() for member in team.members]

    def test_get_team_member_for_nonexistent_event(self, logged_in_client):
        response = logged_in_client.get(self.get_endpoint(9999))

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_team_members_include_name_enrichment(self, logged_in_client, user, event_factory, team_factory):
        """Test that team members endpoint includes enriched names (team_name, event_name)"""
        event = event_factory(name="Summer CTF 2024", public=True)
        team = team_factory(event=event, members=[user], name="Elite Hackers")

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify name enrichment is working
        member_data = data["data"][0]
        assert "team_name" in member_data
        assert "event_name" in member_data
        assert member_data["team_name"] == "Elite Hackers"
        assert member_data["event_name"] == "Summer CTF 2024"

        # Verify IDs are still present
        assert member_data["team_id"] == team.id
        assert member_data["event_id"] == event.id


class Test_Event_Team_Management:
    def test_captain_promote(self, team_captain_client):
        """Test that the team promote endpoint works correctly."""

        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/promote",
            json = {"user_id": 3}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]

    def test_captain_promote_invalid_user(self, team_captain_client):
        """Test that the team promote endpoint fails with invalid user."""

        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/promote",
            json = {"user_id": 9999}
        )
        assert response.status_code == 404
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data

    def test_captain_promote_self(self, team_captain_client):
        """Test that the team promote endpoint fails when trying to promote self."""
        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/promote",
            json = {"user_id": 2}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "You cannot promote yourself." in data["errors"]["validation"]

    def test_captain_promote_not_privileged(self, team_member_client):
        """Test that the team promote endpoint fails when a non-captain tries to promote."""

        response = team_member_client.post(
            f"/ng/events/{1}/me/team/promote",
            json = {"user_id": 2}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data

    def test_team_captain_promote_event_closed(self, closed_event_client):
        """Test that the team promote endpoint fails when trying to promote in a closed event."""
        response = closed_event_client.post(
            f"/ng/events/{1}/me/team/promote",
            json = {"user_id": 3}
        )
        print(response.get_json())
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data

    def test_captain_kick(self, team_captain_client):
        """Test that the team kick endpoint works correctly."""

        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": 3}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]

        # Verify that the user is no longer a member of the team
        response = team_captain_client.get(f"/ng/events/{1}/me/team/members")
        assert response.status_code == 200
        members_data = response.get_json()["data"]
        assert len(members_data) == 2

    def test_captain_kick_self(self, team_captain_client):
        """Test that the team kick endpoint fails when trying to kick self."""
        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": 2}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "You cannot kick yourself from the team." in data["errors"][
            "validation"]

    def test_captain_kick_invalid_user(self, team_captain_client):
        """Test that the team kick endpoint fails with invalid user."""
        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": 9999}
        )
        assert response.status_code == 404
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data

    def test_captain_kick_not_privileged(self, team_member_client):
        """Test that the team kick endpoint fails when a non-captain tries to kick."""
        response = team_member_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": 2}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data

    def test_cant_kick_from_other_teams(
        self,
        team_captain_client,
        team_factory,
        user_factory
    ):
        """Test that the team kick endpoint fails when trying to kick a user not in the team."""
        other_team = team_factory(
            event_id = 1,
            members = [user_factory(name = "Other User")]
        )
        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": other_team.members[0].user_id}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "not a member of team" in data["errors"]["validation"]

    def test_cant_kick_closed_event(
        self,
        closed_event_client,
        event_factory,
        team_factory
    ):
        """Test that the team kick endpoint fails when trying to kick a user from a closed event."""
        response = closed_event_client.post(
            f"/ng/events/{1}/me/team/kick",
            json = {"user_id": 3}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "You cannot kick team members" in data["errors"]["forbidden"]

    def test_member_leave(self, team_member_client):
        """Test that the team leave endpoint works correctly."""
        response = team_member_client.post(
            f"/ng/events/{1}/me/team/leave",
            json = {}
        )
        assert response.status_code == 200

        reponse = team_member_client.get(f"/ng/events/{1}/me/team")
        assert reponse.status_code == 404

    def test_captain_cant_leave(self, team_captain_client):
        """Test that the team leave endpoint fails for a captain."""
        response = team_captain_client.post(
            f"/ng/events/{1}/me/team/leave",
            json = {}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert (
            "You cannot leave the team as a captain. Please promote another member first."
            in data["errors"]["forbidden"]
        )

    def test_leave_closed_event(self, closed_event_client):
        """Test that the team leave endpoint fails when trying to leave a closed event."""
        response = closed_event_client.post(
            f"/ng/events/{1}/me/team/leave",
            json = {}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "You cannot leave the team after the event has ended." in data[
            "errors"]["forbidden"]

    def test_solo_captain_can_leave(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory,
        db_session
    ):
        """Test that a captain can leave when they are the only member of the team."""
        event = event_factory(name = "Solo Leave Test Event", public = True)
        _team = team_factory(event = event, members = [user])  # Only one member (the captain)

        Demographic.create_demographic(
            user_id = user.id,
            event_id = event.id,
            commit = False
        )
        db_session.commit()

        response = logged_in_client.post(
            f"/ng/events/{event.id}/me/team/leave",
            json = {}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_update_name(self, team_captain_client):
        """Test that the team name can be updated."""
        new_name = "Updated Team Name"
        response = team_captain_client.put(
            f"/ng/events/{1}/me/team/update_name",
            json = {"name": new_name}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["data"]["name"] == new_name


    def test_update_name_event_over(self, closed_event_client):
        """Test that the team name update fails when the event is over."""
        new_name = "Updated Team Name"
        response = closed_event_client.put(
            f"/ng/events/{1}/me/team/update_name",
            json = {"name": new_name}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "You do not have permission to update the team name" in data[
            "errors"]["forbidden"]

class Test_Event_Team_Start:
    def post_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/team/start"

    def test_start_event_for_team(self, team_captain_client):
        response = team_captain_client.post(
            self.post_endpoint(1),
            json = {}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert "start_timestamp" in data["data"]
        assert data["data"]["start_timestamp"] is not None

    def test_start_event_for_team_not_privileged(self, team_member_client):
        response = team_member_client.post(
            self.post_endpoint(1),
            json = {}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "MISSING_ROLE" in data["errors"]["forbidden"]

    def test_start_event_for_team_event_closed(self, closed_event_client):
        response = closed_event_client.post(
            self.post_endpoint(1),
            json = {}
        )
        assert response.status_code == 403
        data = response.get_json()

        assert not data["success"]
        assert "errors" in data
        assert "EVENT_LOCKED" in data["errors"]["forbidden"]

    def test_start_event_for_team_already_started(self, team_captain_client):
        # Start the event first time
        response = team_captain_client.post(
            self.post_endpoint(1),
            json = {}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]

        # Attempt to start the event again
        response = team_captain_client.post(
            self.post_endpoint(1),
            json = {}
        )
        assert response.status_code == 403
        data = response.get_json()
        assert not data["success"]
        assert "errors" in data
        assert "TEAM_HAS_STARTED" in data["errors"]["forbidden"]


class Test_Event_Admin_Register:
    def post_endpoint(self, event_id: int, user_id: int) -> str:
        return f"/ng/admin/events/{event_id}/{user_id}/register"

    def test_admin_register_user_for_event_code(
        self,
        admin_client,
        user_factory,
        event_factory,
        team_factory
    ):
        event = event_factory(name = "Admin Register Event", public = True)
        user = user_factory(name = "testuser", email = "testuser@example.com")
        user2 = user_factory(
            name = "testuser2",
            email = "testuser2@example.com"
        )
        team = team_factory(event = event, members = [user])

        response = admin_client.post(
            self.post_endpoint(event.id,
                               user2.id),
            json = {
                "invite_code": team.invite_code,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data

    def test_admin_register_user_for_event_name(
        self,
        admin_client,
        user,
        event_factory
    ):
        event = event_factory(name = "Admin Register Event", public = True)

        response = admin_client.post(
            self.post_endpoint(event.id,
                               user.id),
            json = {
                "team_name": "Admin Created Team",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_non_admin_fails_registering_user_for_event(
        self,
        logged_in_client,
        user_factory,
        event_factory
    ):
        event = event_factory(name = "Non-Admin Register Event", public = True)
        user = user_factory(name = "testuser", email = "testuser@example.com")

        response = logged_in_client.post(
            self.post_endpoint(event.id,
                               user.id),
            json = {
                "team_name": "Non-Admin Team",
            },
        )
        assert response.status_code == 403

    def test_admin_can_register_user_for_locked_event(
        self,
        admin_client,
        user_factory,
        event_factory,
        team_factory
    ):
        event = event_factory(
            name = "Admin Register Locked Event",
            public = True,
            locked = True
        )
        user = user_factory(name = "testuser", email = "testuser@example.com")
        user2 = user_factory(
            name = "testuser2",
            email = "testuser2@example.com"
        )
        team = team_factory(event = event, members = [user])

        response = admin_client.post(
            self.post_endpoint(event.id,
                               user2.id),
            json = {
                "invite_code": team.invite_code,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data


def test_admin_get_private_event(admin_client, event_factory):
    event = event_factory(name = "Admin Get Private Event", public = False)

    response = admin_client.get(f"/ng/admin/events/{event.id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"] == event.serialize()


class Test_Event_Admin_Get:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/admin/events/{event_id}"

    def test_admin_get_event_details(self, admin_client, event_factory):
        event = event_factory(name = "Admin Get Event", public = True)

        response = admin_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == event.serialize()

    def test_non_admin_get_event_details(
        self,
        logged_in_client,
        event_factory
    ):
        event = event_factory(name = "Non-Admin Get Event", public = True)

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 302


class Test_Event_Admin_Put:
    def put_endpoint(self, event_id: int) -> str:
        return f"/ng/admin/events/{event_id}"

    def test_admin_update_event(self, admin_client, event_factory):
        event = event_factory(name = "Admin Update Event", public = True)
        time = utc_now()

        updated_data = {
            "name": "Updated Event Name",
            "description": "Updated Description",
            "public": False,
            "registration_open": True,
            "max_team_size": 7,
            "start_time": (time + timedelta(hours=1)).isoformat(),
            "end_time": (time + timedelta(hours=2)).isoformat()
        }

        response = admin_client.put(
            self.put_endpoint(event.id),
            json = updated_data
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == updated_data["name"]
        assert data["data"]["description"] == updated_data["description"]
        assert data["data"]["public"] is False
        assert data["data"]["start_time"] == updated_data["start_time"][:-6] + "Z"
        assert data["data"]["end_time"] == updated_data["end_time"][:-6] + "Z"

    def test_non_admin_update_event(self, logged_in_client, event_factory):
        event = event_factory(name = "Non-Admin Update Event", public = True)

        updated_data = {
            "name": "Updated Event Name",
            "description": "Updated Description",
            "public": False,
        }

        response = logged_in_client.put(
            self.put_endpoint(event.id),
            json = updated_data
        )

        assert response.status_code == 403


class Test_Event_Admin_Create:
    def post_endpoint(self) -> str:
        return "/ng/admin/events"

    def test_admin_create_event(self, admin_client):
        time = utc_now()

        new_event_data = {
            "name": "New Admin Created Event",
            "description": "This is a test event created by admin.",
            "public": True,
            "registration_open": True,
            "max_team_size": 5,
            "start_time": (time + timedelta(hours=1)).isoformat(),
            "end_time": (time + timedelta(hours=2)).isoformat()
        }

        response = admin_client.post(
            self.post_endpoint(),
            json = new_event_data
        )
        print(response.get_json())

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == new_event_data["name"]
        assert data["data"]["description"] == new_event_data["description"]
        assert data["data"]["public"] is True
        assert data["data"]["start_time"] == new_event_data["start_time"][:-6] + "Z"
        assert data["data"]["end_time"] == new_event_data["end_time"][:-6] + "Z"

    def test_non_admin_create_event(self, logged_in_client):
        new_event_data = {
            "name": "New Non-Admin Created Event",
            "description": "This is a test event created by non-admin.",
            "public": True,
            "registration_open": True,
            "max_team_size": 5,
        }

        response = logged_in_client.post(
            self.post_endpoint(),
            json = new_event_data
        )

        assert response.status_code == 403

    def test_admin_create_event_with_missing_fields(self, admin_client):
        new_event_data = {
            "name": "Incomplete Event",
            # Missing description and public fields
        }

        response = admin_client.post(
            self.post_endpoint(),
            json = new_event_data
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "validation" in data["errors"]


class Test_Event_Challenge_Import:
    def get_endpoint(self, event) -> str:
        return f"/ng/admin/events/{event.id}/challenges"

    def test_challenge_import_endpoint(self, admin_client, event):
        with open(os.path.join(os.path.dirname(__file__),
                               "../../challenge/tests/yamls/default.yaml"),
                  "rb") as f:
            yaml = base64.urlsafe_b64encode(f.read())

        response = admin_client.post(
            self.get_endpoint(event),
            json = {"yaml": yaml.decode("utf-8")}
        )

        challenge = Challenge.query.filter_by(name = "Basic Challenge").first()

        assert response.status_code == 200
        assert len(challenge.hints) == 1
        assert len(challenge.questions) == 1

    def test_challenge_import_endpoint_bad_yaml(self, admin_client, event):
        with open(os.path.join(os.path.dirname(__file__),
                               "../../challenge/tests/yamls/bad.yaml"),
                  "rb") as f:
            yaml = base64.urlsafe_b64encode(f.read())

        response = admin_client.post(
            self.get_endpoint(event),
            json = {"yaml": yaml.decode("utf-8")}
        )
        assert response.status_code == 400


class Test_Event_Challenge_List:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/challenges"


    def test_list_challenges_for_event(self, started_player_client, challenge_factory):
        challenge1 = challenge_factory(event_id=1, name="Challenge 1")
        challenge2 = challenge_factory(event_id=1, name="Challenge 2")


        response = started_player_client.get(self.get_endpoint(challenge1.event_id))
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == challenge1.name
        assert data["data"][1]["name"] == challenge2.name

    def test_challenges_include_name_enrichment(self, started_player_client, challenge_factory):
        """Test that challenges endpoint includes enriched names (event_name)"""

        challenge = challenge_factory(event_id=1, name="RSA Decryption")

        response = started_player_client.get(self.get_endpoint(challenge.event_id))
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify name enrichment is working
        challenge_data = data["data"][0]
        assert "event_name" in challenge_data
        assert challenge_data["event_name"] == "Test Event 1"

        # Verify IDs are still present
        assert challenge_data["event_id"] == challenge.event_id
        assert challenge_data["name"] == "RSA Decryption"


class Test_Event_Challenge_Render:
    def get_endpoint(self, event_id: int, challenge_id: int) -> str:
        return f"/ng/events/{event_id}/challenges/{challenge_id}"

    def test_render_challenge_for_event(self, started_player_client, challenge_factory):
        challenge = challenge_factory(event_id=1, name="Challenge to Render")

        response = started_player_client.get(self.get_endpoint(challenge.event_id, challenge.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        # Check that all required render components are present
        render_data = data["data"]
        assert "challenge" in render_data
        assert "questions" in render_data
        assert "hints" in render_data
        assert "attempts" in render_data

        # Verify challenge data
        assert render_data["challenge"] == challenge.serialize()
        assert render_data["challenge"]["name"] == "Challenge to Render"
        assert render_data["challenge"]["event_id"] == challenge.event_id

        # Verify questions are included
        assert len(render_data["questions"]) == 2
        for question in render_data["questions"]:
            assert question["challenge_id"] == challenge.id

        # Verify hints and attempts are present
        assert isinstance(render_data["hints"], list)
        assert isinstance(render_data["attempts"], list)


class Test_Event_Challenge_Statuses:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/challenges"

    def test_get_challenge_statuses_for_event(
        self, started_player_client,challenge_factory
    ):
        challenge1 = challenge_factory(event_id=1, name="Challenge 1")
        challenge2 = challenge_factory(event_id=1, name="Challenge 2")


        response = started_player_client.get(self.get_endpoint(1))
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        assert len(data["data"]) == 2
        assert data["data"][0]["challenge_id"] == challenge1.id
        assert data["data"][1]["challenge_id"] == challenge2.id

        # Verify all required fields are present in challenge progress data
        for challenge_progress in data["data"]:
            assert "challenge_id" in challenge_progress
            assert "challenge_name" in challenge_progress
            assert "challenge_icon" in challenge_progress
            assert "total_points_available" in challenge_progress
            assert "total_points_scored" in challenge_progress
            assert "num_questions_solved" in challenge_progress
            assert "num_questions_available" in challenge_progress
            assert "num_attempts_made" in challenge_progress
            assert "num_unique_questions_attempted" in challenge_progress
            assert "is_completed" in challenge_progress

        # Verify initial state for new challenges (no attempts yet)
        challenge1_progress = data["data"][0]
        challenge2_progress = data["data"][1]

        assert challenge1_progress["challenge_name"] == "Challenge 1"
        assert challenge2_progress["challenge_name"] == "Challenge 2"

        # 2 questions
        assert challenge1_progress["total_points_available"] == 300
        assert challenge2_progress["total_points_available"] == 300

        # No attempts made yet, so scored points should be 0
        assert challenge1_progress["total_points_scored"] == 0
        assert challenge2_progress["total_points_scored"] == 0

        # No questions solved yet
        assert challenge1_progress["num_questions_solved"] == 0
        assert challenge2_progress["num_questions_solved"] == 0

        # Each challenge has 2 questions
        assert challenge1_progress["num_questions_available"] == 2
        assert challenge2_progress["num_questions_available"] == 2

        # No attempts made yet
        assert challenge1_progress["num_attempts_made"] == 0
        assert challenge2_progress["num_attempts_made"] == 0

        # No questions attempted yet
        assert challenge1_progress["num_unique_questions_attempted"] == 0
        assert challenge2_progress["num_unique_questions_attempted"] == 0

        # Not completed yet
        assert challenge1_progress["is_completed"] is False
        assert challenge2_progress["is_completed"] is False

    def test_challenge_statuses_include_challenge_name(
        self, started_player_client,challenge_factory

    ):
        """
        Test that challenge statuses response includes challenge names
        """
        challenge1 = challenge_factory(event_id=1, name="Web Security Challenge")
        challenge2 = challenge_factory(event_id=1, name="Crypto Puzzle")

        response = started_player_client.get(f"/ng/events/{challenge1.event_id}/me/challenges")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2

        # Check that challenge names are included
        challenge_statuses = data["data"]
        challenge1_status = next(
            cs for cs in challenge_statuses
            if cs["challenge_id"] == challenge1.id
        )
        challenge2_status = next(
            cs for cs in challenge_statuses
            if cs["challenge_id"] == challenge2.id
        )

        assert challenge1_status["challenge_name"] == "Web Security Challenge"
        assert challenge2_status["challenge_name"] == "Crypto Puzzle"

        # Also verify the structure includes both id and name
        for status in challenge_statuses:
            assert "challenge_id" in status
            assert "challenge_name" in status
            assert "total_points_available" in status
            assert "num_questions_available" in status

    def test_challenge_progress_with_scoring_integration(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory,
        challenge_factory,
        question_factory,
        attempt_factory
    ):
        """
        Test challenge progress endpoint with actual scoring system integration
        """
        event = event_factory(
            name = "Scoring Integration Test Event",
            public = True
        )
        team = team_factory(event = event, members = [user])
        team.set_start_timestamp(utc_now())

        web_challenge = challenge_factory(event = event, name = "Web Security")
        crypto_challenge = challenge_factory(
            event = event,
            name = "Cryptography"
        )

        web_q1, web_q2 = web_challenge.questions
        crypto_q1, crypto_q2 = crypto_challenge.questions

        # Correct attempt for web_q1
        attempt_factory(
            user_id = user.id,
            team_id = team.id,
            event_id = event.id,
            challenge_id = web_challenge.id,
            question_id = web_q1.id,
            submission = web_q1.answer,
            is_correct = True,
            points = 100
        )

        # Wrong attempt for web_q2
        attempt_factory(
            user_id = user.id,
            team_id = team.id,
            event_id = event.id,
            challenge_id = web_challenge.id,
            question_id = web_q2.id,
            submission = "wrong_sql",
            is_correct = False,
            points = 0
        )

        # Correct attempt for crypto_q1
        attempt_factory(
            user_id = user.id,
            team_id = team.id,
            event_id = event.id,
            challenge_id = crypto_challenge.id,
            question_id = crypto_q1.id,
            submission = crypto_q1.answer,
            is_correct = True,
            points = 100
        )

        # Get challenge progress
        response = logged_in_client.get(f"/ng/events/{event.id}/me/challenges")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2

        # Find progress for each challenge
        web_progress = next(
            c for c in data["data"] if c["challenge_id"] == web_challenge.id
        )
        crypto_progress = next(
            c for c in data["data"] if c["challenge_id"] == crypto_challenge.id
        )

        # Verify web challenge progress
        assert web_progress["challenge_name"] == "Web Security"
        assert web_progress["challenge_icon"] == web_challenge.icon
        assert web_progress["total_points_available"] == 300  # 100 + 200
        assert web_progress["total_points_scored"] == 100  # Only q1 solved
        assert web_progress["num_questions_solved"] == 1  # Only q1 solved
        assert web_progress["num_questions_available"] == 2  # q1 + q2
        assert web_progress["num_attempts_made"] == 2  # 1 correct + 1 wrong
        assert web_progress["num_unique_questions_attempted"] == 2  # Both questions attempted
        assert web_progress["is_completed"] is False  # Not all questions solved

        # Verify crypto challenge progress
        assert crypto_progress["challenge_name"] == "Cryptography"
        assert crypto_progress["challenge_icon"] == crypto_challenge.icon
        assert crypto_progress["total_points_available"] == 300  # 100 + 200
        assert crypto_progress["total_points_scored"] == 100  # Only q1 solved (q1 has 100pts, not 200)
        assert crypto_progress["num_questions_solved"] == 1  # Only q1 solved
        assert crypto_progress["num_questions_available"] == 2  # q1 + q2
        assert crypto_progress["num_attempts_made"] == 1  # 1 correct attempt
        assert crypto_progress["num_unique_questions_attempted"] == 1  # Only q1 attempted
        assert crypto_progress["is_completed"] is False  # Not all questions solved

        # Test completion scenario - solve remaining questions
        attempt_factory(
            user_id = user.id,
            team_id = team.id,
            event_id = event.id,
            challenge_id = web_challenge.id,
            question_id = web_q2.id,
            submission = web_q2.answer,
            is_correct = True,
            points = 200
        )

        attempt_factory(
            user_id = user.id,
            team_id = team.id,
            event_id = event.id,
            challenge_id = crypto_challenge.id,
            question_id = crypto_q2.id,
            submission = crypto_q2.answer,
            is_correct = True,
            points = 200
        )

        response = logged_in_client.get(f"/ng/events/{event.id}/me/challenges")
        assert response.status_code == 200
        data = response.get_json()

        web_progress = next(
            c for c in data["data"] if c["challenge_id"] == web_challenge.id
        )
        crypto_progress = next(
            c for c in data["data"] if c["challenge_id"] == crypto_challenge.id
        )

        assert web_progress["total_points_scored"] == 300  # 100 + 200
        assert web_progress["num_questions_solved"] == 2  # Both solved
        assert web_progress["is_completed"] is True  # All questions solved

        assert crypto_progress["total_points_scored"] == 300  # 100 + 200
        assert crypto_progress["num_questions_solved"] == 2  # Both solved
        assert crypto_progress["is_completed"] is True  # All questions solved

    def test_challenge_progress_no_attempts(
        self,
        logged_in_client,
        user,
        event_factory,
        team_factory,
        challenge_factory
    ):
        """
        Test challenge progress with challenges that have no attempts
        """
        event = event_factory(name = "No Attempts Test Event", public = True)
        _team = team_factory(event = event, members = [user])
        _team.set_start_timestamp(utc_now())
        challenge = challenge_factory(
            event = event,
            name = "Untouched Challenge"
        )

        response = logged_in_client.get(f"/ng/events/{event.id}/me/challenges")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1

        progress = data["data"][0]
        assert progress["challenge_id"] == challenge.id
        assert progress["challenge_name"] == "Untouched Challenge"
        assert progress["total_points_scored"] == 0
        assert progress["num_questions_solved"] == 0
        assert progress["num_attempts_made"] == 0
        assert progress["num_unique_questions_attempted"] == 0
        assert progress["is_completed"] is False
