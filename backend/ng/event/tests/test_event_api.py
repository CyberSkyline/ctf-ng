from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from datetime import datetime, timedelta

class Test_Public_Event_Listing:
    endpoint = "/ng/events"

    def test_list_public_events(self, logged_in_client, event_factory):
        event1 = event_factory(name="Public Event 1", public=True)
        event2 = event_factory(name="Public Event 2", public=True)

        response = logged_in_client.get(self.endpoint)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0] == event1.serialize()
        assert data["data"][1] == event2.serialize()

class Test_Public_Event_Detail:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}"

    def test_get_event_details(self, logged_in_client, event_factory):
        event = event_factory(name="Event for Detail Test", public=True)
        
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

class Test_Event_Eligibility:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/eligibility"

    def test_check_event_eligibility(self, logged_in_client, event_factory):
        event = event_factory(name="Eligible Event", public=True)

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

class Test_Event_Registration:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/register"

    def test_register_for_event_with_new_team(self, logged_in_client, user, event_factory):
        event = event_factory(name="Event for Registration", public=True)

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "Test Team",
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        
        team = Team.query.filter_by(name="Test Team", event_id=event.id).first()
        assert data["data"] == team.serialize()

        team_member = TeamMember.query.filter_by(user_id=user.id, team_id=team.id).first()
        assert team_member is not None

    def test_register_for_event_with_existing_team(self, logged_in_client, user_factory, event_factory, team_factory):
        event = event_factory(name="Event for Existing Team Registration", public=True)
        user = user_factory(name="testuser", email="testuser@example.com")
        existing_team = team_factory(event=event, members=[user])

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "invite_code": existing_team.invite_code,
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        
        team = Team.query.filter_by(id=existing_team.id).first()
        assert data["data"] == team.serialize()

        team_member = TeamMember.query.filter_by(user_id=user.id, team_id=team.id).first()
        assert team_member is not None

    def test_register_member_name_cannot_be_in_team_name(self, logged_in_client, user, event_factory):
        event = event_factory(name="Event for Invalid Team Name", public=True)

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": user.name,
        })

        assert response.status_code == 400
        data = response.get_json()
        print(data)
        assert data["success"] is False
        assert "errors" in data
        assert "Team name cannot include a member's name." in data["errors"]["validation"]

    def test_register_for_nonexistent_event(self, logged_in_client):
        response = logged_in_client.post(self.get_endpoint(9999), json={
            "team_name": "Test Team",
        })

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_register_without_team_name_or_invite_code(self, logged_in_client, event_factory):
        event = event_factory(name="Event for Missing Team Info", public=True)

        response = logged_in_client.post(self.get_endpoint(event.id), json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data

    def test_register_closed_event(self, logged_in_client, event_factory):
        event = event_factory(name="Closed Event", public=True, registration_open=False)

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "Test Team",
        })
        print(response.get_json())

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration is closed." in data["errors"]["business_logic"]

    def test_register_event_before_start(self, logged_in_client, event_factory):
        event = event_factory(name="Event Before Start", public=True, registration_start_date=datetime.utcnow() + timedelta(days=1),registration_end_date=datetime.utcnow() + timedelta(days=2))

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "Test Team",
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has not started yet." in data["errors"]["business_logic"]

    def test_register_event_after_end(self, logged_in_client, event_factory):
        event = event_factory(name="Event After End", public=True, registration_end_date=datetime.utcnow() - timedelta(days=1), registration_start_date=datetime.utcnow() - timedelta(days=2))

        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "Test Team",
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "Event registration has ended." in data["errors"]["business_logic"]

    def test_register_twice_for_event(self, logged_in_client, user, event_factory):
        event = event_factory(name="Event for Duplicate Registration", public=True)

        # First registration
        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "First Team",
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        # Second registration attempt
        response = logged_in_client.post(self.get_endpoint(event.id), json={
            "team_name": "Second Team",
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "User is already registered for this event." in data["errors"]["business_logic"]

class Test_Event_Team_Lookup:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/team"

    def test_get_team_for_event(self, logged_in_client, user, event_factory, team_factory):
        event = event_factory(name="Event for Team Lookup", public=True)
        team = team_factory(event=event, members=[user])

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

    def test_get_team_member_for_event(self, logged_in_client, user, event_factory, team_factory):
        event = event_factory(name="Event for Team Member Lookup", public=True)
        team = team_factory(event=event, members=[user])

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


class Test_Event_Team_Management:

    def test_captain_promote(self, team_captain_client):
        """Test that the team promote endpoint works correctly."""


        response = team_captain_client.post(f"/ng/events/{1}/me/team/promote", json={"user_id": 3})
        print(response.get_json())
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']

    def test_captain_promote_invalid_user(self, team_captain_client):
        """Test that the team promote endpoint fails with invalid user."""

        response = team_captain_client.post(f"/ng/events/{1}/me/team/promote", json={"user_id": 9999})
        assert response.status_code == 404
        data = response.get_json()
        assert not data['success']
        assert "errors" in data

    def test_captain_promote_self(self, team_captain_client):
        """Test that the team promote endpoint fails when trying to promote self."""
        response = team_captain_client.post(f"/ng/events/{1}/me/team/promote", json={"user_id": 2})
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']
        assert "errors" in data
        assert "You cannot promote yourself." in data['errors']['validation']

    def test_captain_promote_not_privileged(self, team_member_client):
        """Test that the team promote endpoint fails when a non-captain tries to promote."""

        response = team_member_client.post(f"/ng/events/{1}/me/team/promote", json={"user_id": 2})
        assert response.status_code == 403
        data = response.get_json()
        assert not data['success']
        assert "errors" in data

    def test_captain_kick(self, team_captain_client):
        """Test that the team kick endpoint works correctly."""

        response = team_captain_client.post(f"/ng/events/{1}/me/team/kick", json={"user_id": 3})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']

        # Verify that the user is no longer a member of the team
        response = team_captain_client.get(f"/ng/events/{1}/me/team/members")
        assert response.status_code == 200
        members_data = response.get_json()['data']
        assert len(members_data) == 2

    def test_captain_kick_self(self, team_captain_client):
        """Test that the team kick endpoint fails when trying to kick self."""
        response = team_captain_client.post(f"/ng/events/{1}/me/team/kick", json={"user_id": 2})
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']
        assert "errors" in data
        assert "You cannot kick yourself from the team." in data['errors']['validation']
    
    def test_captain_kick_invalid_user(self, team_captain_client):
        """Test that the team kick endpoint fails with invalid user."""
        response = team_captain_client.post(f"/ng/events/{1}/me/team/kick", json={"user_id": 9999})
        assert response.status_code == 404
        data = response.get_json()
        assert not data['success']
        assert "errors" in data

    def test_captain_kick_not_privileged(self, team_member_client):
        """Test that the team kick endpoint fails when a non-captain tries to kick."""
        response = team_member_client.post(f"/ng/events/{1}/me/team/kick", json={"user_id": 2})
        assert response.status_code == 403
        data = response.get_json()
        assert not data['success']
        assert "errors" in data

    def test_member_leave(self, team_member_client):
        """Test that the team leave endpoint works correctly."""
        response = team_member_client.get(f"/ng/events/{1}/me/team/leave")
        assert response.status_code == 303
        reponse = team_member_client.get(f"/ng/events/{1}/me/team")
        assert reponse.status_code == 404

        

    def test_member_leave_deletes_team(self, team_member_client, admin_client):
        """Test that leaving a team deletes the team if the user is the last member."""
        #Figure this out later
        pass

    def test_captain_cant_leave(self, team_captain_client):
        """Test that the team leave endpoint fails for a captain."""
        response = team_captain_client.get(f"/ng/events/{1}/me/team/leave")
        assert response.status_code == 403
        data = response.get_json()
        assert not data['success']
        assert "errors" in data
        assert "You cannot leave the team as a captain. Please promote another member first." in data['errors']['forbidden']


class Test_Event_Admin_Register:
    def post_endpoint(self, event_id: int, user_id: int) -> str:
        return f"/ng/admin/events/{event_id}/{user_id}/register"

    def test_admin_register_user_for_event_code(self, admin_client, user_factory, event_factory, team_factory):
        event = event_factory(name="Admin Register Event", public=True)
        user = user_factory(name="testuser", email="testuser@example.com")
        user2 = user_factory(name="testuser2", email="testuser2@example.com")
        team = team_factory(event=event, members=[user])

        response = admin_client.post(self.post_endpoint(event.id, user2.id), json={
            "invite_code": team.invite_code,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
    def test_admin_register_user_for_event_name(self, admin_client, user, event_factory):
        event = event_factory(name="Admin Register Event", public=True)

        response = admin_client.post(self.post_endpoint(event.id, user.id), json={
            "team_name": "Admin Created Team",
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
