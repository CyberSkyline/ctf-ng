from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember

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

    def test_register_for_event_with_existing_team(self, logged_in_client, user, event_factory, team_factory):
        event = event_factory(name="Event for Existing Team Registration", public=True)
        existing_team = team_factory(event=event)

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
