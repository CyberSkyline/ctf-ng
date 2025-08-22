"""
Tests for scoring API endpoints
"""

import json
import pytest
from datetime import datetime


class TestUserScoringEndpoints:
    """Tests for user scoring API endpoints"""

    def test_get_leaderboard_basic(self, logged_in_client, event, multiple_teams_with_scores):
        """Test getting basic leaderboard"""
        response = logged_in_client.get(f"/ng/events/{event.id}/leaderboard")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 5

        # Should be ordered by points descending
        points = [team["points"] for team in data["data"]]
        assert points == sorted(points, reverse=True)

    def test_get_leaderboard_with_limit(self, logged_in_client, event, multiple_teams_with_scores):
        """Test getting leaderboard with limit"""
        response = logged_in_client.get(f"/ng/events/{event.id}/leaderboard?limit=3")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 3

    def test_get_leaderboard_invalid_limit(self, logged_in_client, event):
        """Test getting leaderboard with invalid limit"""
        response = logged_in_client.get(f"/ng/events/{event.id}/leaderboard?limit=0")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_leaderboard_limit_too_high(self, logged_in_client, event):
        """Test getting leaderboard with limit too high"""
        response = logged_in_client.get(f"/ng/events/{event.id}/leaderboard?limit=2000")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_leaderboard_nonexistent_event(self, logged_in_client):
        """Test getting leaderboard for nonexistent event"""
        response = logged_in_client.get("/ng/events/999999/leaderboard")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_my_team_score_basic(self, logged_in_client, user, event, team_with_member, score):
        """Test getting my team's score"""
        response = logged_in_client.get(f"/ng/events/{event.id}/me/team/score")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert "points" in data["data"]
        assert "team_id" in data["data"]
        assert "event_id" in data["data"]

    def test_get_my_team_score_with_history(self, logged_in_client, user, event, team_with_member, score, score_event):
        """Test getting my team's score with history"""
        response = logged_in_client.get(f"/ng/events/{event.id}/me/team/score?include_history=true")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert "points" in data["data"]
        assert data["data"]["points"] == 50  # From the score_event fixture

    def test_get_my_team_score_no_team(self, logged_in_client, event):
        """Test getting my team's score when not in a team"""
        response = logged_in_client.get(f"/ng/events/{event.id}/me/team/score")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_my_team_score_nonexistent_event(self, logged_in_client):
        """Test getting my team's score for nonexistent event"""
        response = logged_in_client.get("/ng/events/999999/me/team/score")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_submit_answer_correct(self, team_captain_client, user, event, challenge, question, permissions):
        """Test submitting correct answer"""
        response = team_captain_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            json={"submission": question.answer},
        )

        if response.status_code != 201:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.get_json()}")

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["is_correct"] is True
        assert data["data"]["points"] == question.points

    def test_submit_answer_incorrect(self, team_captain_client, user, event, challenge, question, permissions):
        """Test submitting incorrect answer"""
        response = team_captain_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            json={"submission": "wrong answer"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["is_correct"] is False
        assert data["data"]["points"] == 0

    def test_submit_answer_no_team(self, logged_in_client, event, challenge, question):
        """Test submitting answer when not in a team"""
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            json={"submission": "test"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_submit_answer_missing_submission(
        self, logged_in_client, user, event, team_with_member, challenge, question, permissions
    ):
        """Test submitting answer without submission data"""
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit", json={}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_submit_answer_empty_submission(self, logged_in_client, user, event, team_with_member, challenge, question, permissions):
        """Test submitting empty answer"""
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            json={"submission": "   "},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_submit_answer_invalid_json(self, logged_in_client, user, event, team_with_member, challenge, question):
        """Test submitting answer with invalid JSON"""
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            data="invalid json",
            content_type="application/json",
        )

        # CTFd's CSRF middleware catches malformed JSON before our validation runs
        assert response.status_code == 403

    def test_submit_answer_nonexistent_question(self, logged_in_client, user, event, team_with_member, challenge):
        """Test submitting answer to nonexistent question"""
        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/999999/submit", json={"submission": "test"}
        )

        assert response.status_code == 404  # Middleware returns 404 for not found
        data = response.get_json()
        assert data["success"] is False

    def test_submit_answer_max_attempts_reached(
        self, team_captain_client, user, event, challenge, question, permissions
    ):
        """Test submitting answer when max attempts reached"""
        # Submit max attempts
        for i in range(question.max_attempts):
            response = team_captain_client.post(
                f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
                json={"submission": f"attempt{i}"},
            )
            assert response.status_code == 201

        # Try one more - should fail
        response = team_captain_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            json={"submission": "final attempt"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_redeem_hint_success(self, team_captain_client, user, event, challenge, hint, permissions):
        """Test successfully redeeming a hint"""
        # Get the CSRF token (nonce) from the session
        with team_captain_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = team_captain_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/hint/{hint.id}/redeem", data={"nonce": nonce}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True

        assert data["data"]["id"] == hint.id
        assert data["data"]["body"] == hint.body
        assert data["data"]["preview"] == hint.preview
        assert data["data"]["is_redeemed"] is True
        assert data["data"]["deduction"] == hint.deduction

    def test_redeem_hint_no_team(self, logged_in_client, event, challenge, hint):
        """Test redeeming hint when not in a team"""

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/hint/{hint.id}/redeem", data={"nonce": nonce}
        )

        assert response.status_code == 404  # load_team_by_user_and_event returns 404
        data = response.get_json()
        assert data["success"] is False

    def test_redeem_hint_already_redeemed(self, team_captain_client, challenge_factory, hint_factory, permissions):
        """Test redeeming hint that was already redeemed"""
        # Get the CSRF token (nonce) from the session
        with team_captain_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        challenge = challenge_factory(event_id=1)
        hint = hint_factory(challenge_id=challenge.id)

        # First redemption
        response = team_captain_client.post(
            f"/ng/events/{challenge.event_id}/challenges/{challenge.id}/hint/{hint.id}/redeem", data={"nonce": nonce}
        )
        assert response.status_code == 201

        # Get a fresh nonce for the second redemption
        with team_captain_client.session_transaction() as sess:
            fresh_nonce = sess.get("nonce")

        # Second redemption should fail
        response = team_captain_client.post(
            f"/ng/events/{challenge.event_id}/challenges/{challenge.id}/hint/{hint.id}/redeem", data={"nonce": fresh_nonce}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_redeem_hint_nonexistent_hint(self, logged_in_client, user, event, team_with_member, challenge):
        """Test redeeming nonexistent hint"""
        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/events/{event.id}/challenges/{challenge.id}/hint/999999/redeem", data={"nonce": nonce}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_redeem_hint_locked_event(self, logged_in_client, user, team_with_member, locked_event, challenge, hint):
        """Test redeeming hint for locked event"""
        # Create team in locked event
        from ...team.models.Team import Team

        Team.create_team_with_captain(
            name="Locked Team", event_id=locked_event.id, captain_id=user.id, invite_code="locked123"
        )

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/events/{locked_event.id}/challenges/{challenge.id}/hint/{hint.id}/redeem", data={"nonce": nonce}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_hint_visibility_through_challenge_endpoint(self, team_captain_client, challenge_factory, hint_factory, permissions):
        """
        Test that hints are hidden before redemption and visible after through challenge endpoint
        """
        challenge = challenge_factory(event_id=1)
        hint = hint_factory(challenge_id=challenge.id)
        response = team_captain_client.get(f"/ng/events/{challenge.event_id}/challenges/{challenge.id}")
        assert response.status_code == 200
        data = response.get_json()

        hints = data["data"]["hints"]
        hint_data = next((h for h in hints if h["id"] == hint.id), None)
        assert hint_data is not None

        assert hint_data["body"] is None
        assert hint_data["preview"] == hint.preview
        assert hint_data["is_redeemed"] is False

        with team_captain_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        redeem_response = team_captain_client.post(
            f"/ng/events/{challenge.event_id}/challenges/{challenge.id}/hint/{hint.id}/redeem",
            data={"nonce": nonce}
        )
        assert redeem_response.status_code == 201

        response = team_captain_client.get(f"/ng/events/{challenge.event_id}/challenges/{challenge.id}")
        assert response.status_code == 200
        data = response.get_json()

        hints = data["data"]["hints"]
        hint_data_after = next((h for h in hints if h["id"] == hint.id), None)
        assert hint_data_after is not None

        assert hint_data_after["body"] == hint.body
        assert hint_data_after["preview"] == hint.preview
        assert hint_data_after["is_redeemed"] is True


    def test_unauthenticated_requests(self, client, event, challenge, question, hint):
        """Test that unauthenticated requests fail"""
        endpoints = [
            f"/ng/events/{event.id}/leaderboard",
            f"/ng/events/{event.id}/me/team/score",
            f"/ng/events/{event.id}/challenges/{challenge.id}/questions/{question.id}/submit",
            f"/ng/events/{event.id}/challenges/{challenge.id}/hint/{hint.id}/redeem",
        ]

        for endpoint in endpoints:
            if "submit" in endpoint or "redeem" in endpoint:
                response = client.post(endpoint, json={"submission": "test"})
            else:
                response = client.get(endpoint)

            # CTFd returns either 302 or 403 for unauthenticated requests depending on test order
            # Meaning, admin auth test runs first, state somehow isnt reset (working on debugging)
            # and normal auth would redirect and vise versa, therefore, these codes are flipped 50/50
            # Either way though, it still confirms: Unauthenticated = Not accessed/Redirection
            # Regardless of what status code (302 vs 404) - anything else would be a fail
            assert response.status_code in [302, 403]


class TestAdminScoringEndpoints:
    """Tests for admin scoring API endpoints"""

    def test_award_manual_points_positive(self, admin_client, admin, event, team_with_member):
        """Test awarding positive manual points"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            json={"points": 100, "reason": "Excellent teamwork"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["points"] == 100
        assert data["data"]["reason"] == "Excellent teamwork"

    def test_award_manual_points_negative(self, admin_client, admin, event, team_with_member, score):
        """Test awarding negative manual points (penalty)"""
        # Set initial points
        score.points = 200

        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            json={"points": -50, "reason": "Rule violation"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        # Controller returns ManualPointAward object directly
        assert data["data"]["points"] == -50
        assert data["data"]["reason"] == "Rule violation"

    def test_award_manual_points_zero_points_fails(self, admin_client, admin, event, team_with_member):
        """Test that awarding zero points fails"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            json={"points": 0, "reason": "Test"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_award_manual_points_missing_reason(self, admin_client, admin, event, team_with_member):
        """Test awarding points without reason"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points", json={"points": 100}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_award_manual_points_empty_reason(self, admin_client, admin, event, team_with_member):
        """Test awarding points with empty reason"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            json={"points": 100, "reason": "   "},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_award_manual_points_invalid_json(self, admin_client, admin, event, team_with_member):
        """Test awarding points with invalid JSON"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            data="invalid json",
            content_type="application/json",
        )

        # CTFd's CSRF middleware catches malformed JSON before our validation runs
        assert response.status_code == 403

    def test_award_manual_points_nonexistent_team(self, admin_client, admin, event):
        """Test awarding points to nonexistent team"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/999999/award-points", json={"points": 100, "reason": "Test"}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_award_manual_points_nonexistent_event(self, admin_client, admin, team_with_member):
        """Test awarding points for nonexistent event"""
        response = admin_client.post(
            f"/ng/admin/scoring/events/999999/teams/{team_with_member.id}/award-points",
            json={"points": 100, "reason": "Test"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_award_manual_points_non_admin_fails(self, logged_in_client, user, event, team_with_member):
        """Test that non-admin cannot award points"""
        response = logged_in_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            json={"points": 100, "reason": "Test"},
        )

        assert response.status_code in [302, 403]

    def test_recalculate_score_basic(self, admin_client, admin, event, team_with_member, score):
        """Test basic score recalculation"""
        # Manually set score to wrong value
        score.points = 999

        # Get the CSRF token (nonce) from the session
        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/recalculate", data={"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["points"] == 0  # No score events

    def test_recalculate_score_with_events(
        self, admin_client, admin, event, team_with_member, score, score_event_factory
    ):
        """Test recalculating score with score events"""
        # Create score events
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=100)
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=50)

        # Manually set score to wrong value
        score.points = 999

        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/recalculate", data={"nonce": nonce}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["points"] == 150  # 100 + 50

    def test_recalculate_score_nonexistent_team(self, admin_client, admin, event):
        """Test recalculating score for nonexistent team"""

        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = admin_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/999999/recalculate", data={"nonce": nonce}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_recalculate_score_nonexistent_event(self, admin_client, admin, team_with_member):
        """Test recalculating score for nonexistent event"""

        with admin_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = admin_client.post(
            f"/ng/admin/scoring/events/999999/teams/{team_with_member.id}/recalculate", data={"nonce": nonce}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_recalculate_score_non_admin_fails(self, logged_in_client, user, event, team_with_member):
        """Test that non-admin cannot recalculate scores"""

        with logged_in_client.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = logged_in_client.post(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/recalculate", data={"nonce": nonce}
        )

        assert response.status_code in [302, 403]

    def test_get_score_history_basic(self, admin_client, admin, event, team_with_member, score_event):
        """Test getting basic score history"""
        response = admin_client.get(f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    def test_get_score_history_with_limit(
        self, admin_client, admin, event, team_with_member, score, score_event_factory
    ):
        """Test getting score history with limit"""
        # Create multiple score events
        for i in range(10):
            score_event_factory(score_id=score.id, team_id=team_with_member.id, points=10 * (i + 1))

        response = admin_client.get(f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history?limit=5")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 5

    def test_get_score_history_invalid_limit(self, admin_client, admin, event, team_with_member):
        """Test getting score history with invalid limit"""
        response = admin_client.get(f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history?limit=0")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_score_history_limit_too_high(self, admin_client, admin, event, team_with_member):
        """Test getting score history with limit too high"""
        response = admin_client.get(
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history?limit=1000"
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_score_history_nonexistent_team(self, admin_client, admin, event):
        """Test getting score history for nonexistent team"""
        response = admin_client.get(f"/ng/admin/scoring/events/{event.id}/teams/999999/history")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_score_history_nonexistent_event(self, admin_client, admin, team_with_member):
        """Test getting score history for nonexistent event"""
        response = admin_client.get(f"/ng/admin/scoring/events/999999/teams/{team_with_member.id}/history")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_get_score_history_non_admin_fails(self, logged_in_client, user, event, team_with_member):
        """Test that non-admin cannot get score history"""
        response = logged_in_client.get(f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history")

        # CTFd returns 302 redirect for non admin access to admin endpoints in test environment
        assert response.status_code == 302

    def test_get_score_history_empty(self, admin_client, admin, event, team_with_member):
        """Test getting score history for team with no events"""
        # Delete any existing score events
        from ..models import ScoreEvent

        ScoreEvent.query.filter_by(team_id=team_with_member.id).delete()

        response = admin_client.get(f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        # Controller returns empty list when no events
        assert data["data"] == []

    def test_unauthenticated_admin_requests(self, client, event, team_with_member):
        """Test that unauthenticated admin requests fail"""
        endpoints = [
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/award-points",
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/recalculate",
            f"/ng/admin/scoring/events/{event.id}/teams/{team_with_member.id}/history",
        ]

        for endpoint in endpoints:
            if "award-points" in endpoint:
                response = client.post(endpoint, json={"points": 100, "reason": "test"})
            elif "recalculate" in endpoint:
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)

            # CTFd returns either 302 or 403 for unauthenticated requests depending on test order
            # Meaning, admin auth test runs first, state somehow isnt reset (working on debugging)
            # and normal auth would redirect and vise versa, therefore, these codes are flipped 50/50
            # Either way though, it still confirms: Unauthenticated = Not accessed/Redirection
            # Regardless of what status code (302 vs 404) - anything else would be a fail
            assert response.status_code in [302, 403]


class TestScoringAPIIntegration:
    """Integration tests for scoring API endpoints"""

    def test_concurrent_submissions(self, team_captain_client, challenge_factory, permissions):
        """Test handling of concurrent submissions"""
        # Submit multiple answers rapidly
        challenge = challenge_factory(event_id=1)

        responses = []
        for i in range(3):
            response = team_captain_client.post(
                f"/ng/events/1/challenges/{challenge.id}/questions/1/submit",
                json={"submission": f"answer{i}"},
            )
            responses.append(response)

        # All should succeed (until max attempts)
        for response in responses:
            assert response.status_code == 201

        # Check final score is consistent
        response = team_captain_client.get(f"/ng/events/1/me/team/score")
        assert response.status_code == 200
        # Score should be 0 since all were wrong answers
        assert response.get_json()["data"]["points"] == 0


# TODO: Having CTFD issues with more complex integration tests, will come back to this after PR sumbittion and also work on it more during backend clean up, for now, complete flows, individual tests pretyy much cover this
