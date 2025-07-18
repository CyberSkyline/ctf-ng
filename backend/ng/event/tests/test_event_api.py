import base64
import os

from ...challenge.models.Challenge import Challenge
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

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json={
                "team_name": "Test Team",
            },
        )

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

        response = logged_in_client.post(
            self.get_endpoint(event.id),
            json={
                "invite_code": existing_team.invite_code,
            },
        )

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


class Test_Event_Challenge_Import:
    def get_endpoint(self, event) -> str:
        return f"/ng/admin/events/{event.id}/challenges"

    def test_challenge_import_endpoint(self, admin_client, event):
        with open(os.path.join(os.path.dirname(__file__), "../../challenge/tests/yamls/default.yaml"), "rb") as f:
            yaml = base64.urlsafe_b64encode(f.read())

        response = admin_client.post(self.get_endpoint(event), json={"yaml": yaml.decode("utf-8")})

        challenge = Challenge.query.filter_by(name="Basic Challenge").first()

        assert response.status_code == 200
        assert len(challenge.hints) == 1
        assert len(challenge.questions) == 1

    def test_challenge_import_endpoint_bad_yaml(self, admin_client, event):
        with open(os.path.join(os.path.dirname(__file__), "../../challenge/tests/yamls/bad.yaml"), "rb") as f:
            yaml = base64.urlsafe_b64encode(f.read())

        response = admin_client.post(self.get_endpoint(event), json={"yaml": yaml.decode("utf-8")})
        assert response.status_code == 400


class Test_Event_Challenge_List:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/challenges"

    def test_list_challenges_for_event(self, logged_in_client, event_factory, challenge_factory):
        event = event_factory(name="Event for Challenge Listing", public=True)
        challenge1 = challenge_factory(event=event, name="Challenge 1")
        challenge2 = challenge_factory(event=event, name="Challenge 2")

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == challenge1.name
        assert data["data"][1]["name"] == challenge2.name


class Test_Event_Challenge_Render:
    def get_endpoint(self, event_id: int, challenge_id: int) -> str:
        return f"/ng/events/{event_id}/challenges/{challenge_id}"

    def test_render_challenge_for_event(self, logged_in_client, user, event_factory, team_factory, challenge_factory):
        event = event_factory(name="Event for Challenge Rendering", public=True)
        team_factory(event=event, members=[user])
        challenge = challenge_factory(event=event, name="Challenge to Render")

        response = logged_in_client.get(self.get_endpoint(event.id, challenge.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["challenge"] == challenge.serialize()

        # TODO - Add more assertions to check the rendered challenge data


class Test_Event_Challenge_Statuses:
    def get_endpoint(self, event_id: int) -> str:
        return f"/ng/events/{event_id}/me/challenges"

    def test_get_challenge_statuses_for_event(
        self, logged_in_client, user, event_factory, team_factory, challenge_factory
    ):
        event = event_factory(name="Event for Challenge Statuses", public=True)
        team_factory(event=event, members=[user])
        challenge1 = challenge_factory(event=event, name="Challenge 1")
        challenge2 = challenge_factory(event=event, name="Challenge 2")

        response = logged_in_client.get(self.get_endpoint(event.id))

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["challenge_id"] == challenge1.id
        assert data["data"][1]["challenge_id"] == challenge2.id

        # TODO - Add more assertions to check the results
