"""
Tests for feedback API endpoints
"""

from ...team.models.Team import Team
import pytest
from datetime import timedelta
from ...core.utils import utc_now


class TestUserFeedbackEndpoints:
    """
    Test for user feedback API endpoints
    """
    def test_submit_event_feedback_new(self, logged_in_client, user, event, team_with_member: Team):
        """
        Test submitting new event feedback
        """

        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {
                "feedback_data": {
                    "rating": 5,
                    "comments": "Great event!",
                    "difficulty": "medium",
                },
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["user_id"] == user.id
        assert data["data"]["event_id"] == event.id
        assert data["data"]["challenge_id"] is None
        assert data["data"]["feedback_data"]["rating"] == 5
        assert data["data"]["feedback_data"]["comments"] == "Great event!"

    def test_submit_event_feedback_update(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        feedback_factory
    ):
        """
        Test updating existing event feedback
        """
        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        existing_feedback = feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {
                "rating": 3,
                "comments": "OK event"
            },
        )

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {
                "feedback_data": {
                    "rating": 5,
                    "comments": "Actually, great event!",
                },
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == existing_feedback.id
        assert data["data"]["feedback_data"]["rating"] == 5
        assert data["data"]["feedback_data"]["comments"] == "Actually, great event!"

    def test_submit_event_feedback_too_early(self, logged_in_client, user, event, team_with_member: Team):
        """
        Test submitting feedback before team has finished (end_timestamp in future) returns 403
        """
        # team finishes 30 minutes in the future
        team_with_member.start_timestamp = utc_now() - timedelta(hours=1)
        team_with_member.end_time = utc_now() + timedelta(minutes=30)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json={
                "feedback_data": {
                    "rating": 5,
                    "comments": "Too early!",
                },
            },
        )

        assert response.status_code == 403

    def test_submit_event_feedback_not_registered(self, logged_in_client, user, event):
        """
        Test that submitting feedback for an event the user is not registered for produces an error
        """
        # User is not registered for this event (no team_with_member fixture)
        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json={
                "feedback_data": {
                    "rating": 5,
                    "comments": "Should not be allowed",
                },
            },
        )

        assert response.status_code == 404

    def test_get_my_event_feedback(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        feedback_factory
    ):
        """
        Test getting my event feedback
        """
        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 4},
        )

        response = logged_in_client.get(f"/ng/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["user_id"] == user.id
        assert data["data"]["event_id"] == event.id
        assert data["data"]["feedback_data"]["rating"] == 4

    def test_get_my_event_feedback_not_submitted(self, logged_in_client, user, team_with_member: Team, event):
        """
        Test getting event feedback when none submitted
        """
        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        response = logged_in_client.get(f"/ng/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] is None

    def test_submit_challenge_feedback_new(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        challenge
    ):
        """
        Test submitting new challenge feedback
        """
        # team started 1 hour ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
            json = {
                "feedback_data": {
                    "difficulty": "hard",
                    "quality": 5,
                    "comments": "Very challenging!",
                },
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["user_id"] == user.id
        assert data["data"]["event_id"] == event.id
        assert data["data"]["challenge_id"] == challenge.id
        assert data["data"]["feedback_data"]["difficulty"] == "hard"
        assert data["data"]["feedback_data"]["quality"] == 5

    def test_submit_challenge_feedback_update(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        challenge,
        feedback_factory
    ):
        """
        Test updating existing challenge feedback
        """
        # team started 1 hour ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)

        existing_feedback = feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge.id,
            feedback_data = {
                "difficulty": "easy",
                "quality": 3
            },
        )

        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
            json = {
                "feedback_data": {
                    "difficulty": "hard",
                    "quality": 5,
                    "comments": "Changed my mind, it's hard!",
                },
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == existing_feedback.id
        assert data["data"]["feedback_data"]["difficulty"] == "hard"
        assert data["data"]["feedback_data"]["quality"] == 5

    def test_submit_challenge_feedback_too_early(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        challenge
    ):
        """
        Test submitting challenge feedback before team has started returns 403
        """
        # team has no start time (not started)
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
            json={
                "feedback_data": {
                    "difficulty": "hard",
                    "quality": 5,
                    "comments": "Trying to submit too early!",
                },
            },
        )

        assert response.status_code == 403

    def test_submit_challenge_feedback_not_registered(
        self,
        logged_in_client,
        user,
        event,
        challenge
    ):
        """
        Test that submitting challenge feedback for an event the user is not registered for produces a 404
        """
        # User is not registered for this event (no team_with_member fixture)
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
            json={
                "feedback_data": {
                    "difficulty": "medium",
                    "quality": 4,
                    "comments": "Should not be allowed",
                },
            },
        )

        assert response.status_code == 404

    def test_get_my_challenge_feedback(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        challenge,
        feedback_factory
    ):
        """
        Test getting my challenge feedback
        """
        # team started 1 hour ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge.id,
            feedback_data = {"quality": 5},
        )

        response = logged_in_client.get(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["user_id"] == user.id
        assert data["data"]["challenge_id"] == challenge.id
        assert data["data"]["feedback_data"]["quality"] == 5

    def test_get_my_challenge_feedback_not_submitted(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        challenge
    ):
        """
        Test getting challenge feedback when none submitted
        """
        # team started 1 hour ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)

        response = logged_in_client.get(
            f"/ng/events/{event.id}/challenges/{challenge.id}/feedback"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] is None

    def test_submit_event_feedback_nonexistent_event(self, logged_in_client):
        """
        Test submitting feedback for nonexistent event
        """
        response = logged_in_client.post(
            "/ng/events/999999/feedback",
            json = {"feedback_data": {
                "rating": 5
            }},
        )

        assert response.status_code == 404

    def test_submit_challenge_feedback_nonexistent_challenge(
        self,
        logged_in_client,
        event
    ):
        """
        Test submitting feedback for nonexistent challenge
        """
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/999999/feedback",
            json = {"feedback_data": {
                "quality": 5
            }},
        )

        assert response.status_code == 404

    def test_submit_feedback_empty_data(self, logged_in_client, user, team_with_member, event):
        """
        Test submitting feedback with empty feedback_data
        """
        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {"feedback_data": {}},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["feedback_data"] == {}

    def test_submit_feedback_missing_feedback_data(self, logged_in_client, user, team_with_member, event):
        """
        Test submitting feedback without feedback_data field
        """
        # team finished 30 minutes ago
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["feedback_data"] == {}

    def test_unauthenticated_requests(self, client, event, challenge):
        """
        Test that unauthenticated requests fail
        """
        endpoints = [
            (f"/ng/events/{event.id}/feedback",
             "GET",
             None),
            (
                f"/ng/events/{event.id}/feedback",
                "POST",
                {
                    "feedback_data": {
                        "rating": 5
                    }
                },
            ),
            (
                f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
                "GET",
                None,
            ),
            (
                f"/ng/events/{event.id}/challenges/{challenge.id}/feedback",
                "POST",
                {
                    "feedback_data": {
                        "quality": 5
                    }
                },
            ),
        ]

        for endpoint, method, json_data in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json = json_data)

            assert response.status_code in [401, 403]

    def test_get_all_event_feedback(
        self,
        admin_client,
        event,
        user,
        user_factory,
        feedback_factory
    ):
        """
        Test admin getting all event feedback
        """
        user2 = user_factory(name = "User 2", email = "user2@example.com")

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 5},
        )
        feedback_factory(
            user_id = user2.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 3},
        )

        response = admin_client.get(f"/ng/admin/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert all(f["event_id"] == event.id for f in data["data"])
        assert all(f["challenge_id"] is None for f in data["data"])

    def test_get_all_challenge_feedback(
        self,
        admin_client,
        event,
        challenge,
        user,
        user_factory,
        feedback_factory
    ):
        """
        Test admin getting all challenge feedback
        """
        user2 = user_factory(name = "User 2", email = "user2@example.com")

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge.id,
            feedback_data = {"quality": 5},
        )
        feedback_factory(
            user_id = user2.id,
            event_id = event.id,
            challenge_id = challenge.id,
            feedback_data = {"quality": 4},
        )

        response = admin_client.get(
            f"/ng/admin/events/{event.id}/challenges/{challenge.id}/feedback"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert all(f["challenge_id"] == challenge.id for f in data["data"])

    def test_get_event_feedback_empty(self, admin_client, event):
        """
        Test admin getting event feedback when none submitted
        """
        response = admin_client.get(f"/ng/admin/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_get_challenge_feedback_empty(self, admin_client, event, challenge):
        """
        Test admin getting challenge feedback when none submitted
        """
        response = admin_client.get(
            f"/ng/admin/events/{event.id}/challenges/{challenge.id}/feedback"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_get_event_feedback_excludes_challenge_feedback(
        self,
        admin_client,
        event,
        challenge,
        user,
        feedback_factory
    ):
        """
        Test that event feedback endpoint excludes challenge feedback
        """
        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 5},
        )
        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge.id,
            feedback_data = {"quality": 5},
        )

        response = admin_client.get(f"/ng/admin/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["challenge_id"] is None

    def test_get_challenge_feedback_for_specific_challenge(
        self,
        admin_client,
        event,
        challenge_factory,
        user,
        feedback_factory
    ):
        """
        Test that challenge feedback endpoint only returns feedback for that challenge
        """
        challenge1 = challenge_factory(event = event)
        challenge2 = challenge_factory(event = event)

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge1.id,
            feedback_data = {"quality": 5},
        )
        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = challenge2.id,
            feedback_data = {"quality": 3},
        )

        response = admin_client.get(
            f"/ng/admin/events/{event.id}/challenges/{challenge1.id}/feedback"
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["challenge_id"] == challenge1.id

    def test_get_feedback_nonexistent_event(self, admin_client):
        """
        Test admin getting feedback for nonexistent event
        """
        response = admin_client.get("/ng/admin/events/999999/feedback")

        assert response.status_code == 404

    def test_get_feedback_nonexistent_challenge(self, admin_client, event):
        """
        Test admin getting feedback for nonexistent challenge
        """
        response = admin_client.get(
            f"/ng/admin/events/{event.id}/challenges/999999/feedback"
        )

        assert response.status_code == 404

    def test_non_admin_access_fails(self, logged_in_client, event, challenge):
        """
        Test that non-admin cannot access admin endpoints
        """
        endpoints = [
            (f"/ng/admin/events/{event.id}/feedback",
             "GET"),
            (
                f"/ng/admin/events/{event.id}/challenges/{challenge.id}/feedback",
                "GET",
            ),
        ]

        for endpoint, _method in endpoints:
            response = logged_in_client.get(endpoint)
            assert response.status_code in [302, 403]

    def test_feedback_ordered_by_updated_at(
        self,
        admin_client,
        event,
        user_factory,
        feedback_factory,
        db_session
    ):
        """
        Test that admin feedback list is ordered by updated_at desc
        """
        user1 = user_factory(name = "User 1", email = "user1@example.com")
        user2 = user_factory(name = "User 2", email = "user2@example.com")
        user3 = user_factory(name = "User 3", email = "user3@example.com")

        fb1 = feedback_factory(
            user_id = user1.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 5},
        )
        fb2 = feedback_factory(
            user_id = user2.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 4},
        )
        fb3 = feedback_factory(
            user_id = user3.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 3},
        )

        fb1.updated_at = utc_now() - timedelta(hours = 2)
        fb2.updated_at = utc_now() - timedelta(hours = 1)
        fb3.updated_at = utc_now()
        db_session.commit()

        response = admin_client.get(f"/ng/admin/events/{event.id}/feedback")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["data"][0]["user_id"] == user3.id
        assert data["data"][1]["user_id"] == user2.id
        assert data["data"][2]["user_id"] == user1.id

    def test_submit_feedback_data_too_large(self, logged_in_client, event, team_with_member: Team):
        """
        Test that submitting feedback exceeding max serialized size fails
        """
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        long_string = "A" * 50001

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {"feedback_data": {"comments": long_string}},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "50000" in str(data["errors"])

    def test_update_feedback_data_too_large(
        self,
        logged_in_client,
        user,
        event,
        team_with_member: Team,
        feedback_factory
    ):
        """
        Test that updating feedback exceeding max serialized size fails
        """
        team_with_member.start_timestamp = utc_now() - timedelta(hours = 1)
        team_with_member.end_timestamp = utc_now() - timedelta(minutes = 30)

        feedback_factory(
            user_id = user.id,
            event_id = event.id,
            challenge_id = None,
            feedback_data = {"rating": 3},
        )

        long_string = "A" * 50001

        response = logged_in_client.post(
            f"/ng/events/{event.id}/feedback",
            json = {"feedback_data": {"comments": long_string}},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "50000" in str(data["errors"])
