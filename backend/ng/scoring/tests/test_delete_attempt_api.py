"""
Tests for delete attempt API endpoint
"""

import pytest

from ...core.utils import utc_now
from ..models import Attempt, Score


class TestDeleteAttemptEndpoint:
    """
    Tests for DELETE /ng/admin/scoring/attempts/<id>
    """
    def test_delete_attempt_success(
        self,
        admin_client,
        admin,
        user,
        team_with_member,
        event,
        challenge,
        question,
        db_session
    ):
        """
        Test that admin can delete an attempt and score is adjusted
        """
        team_with_member.set_start_timestamp(utc_now())
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )
        db_session.commit()

        score = Score.find_by_team(team_with_member.id)
        initial_score = score.points

        response = admin_client.delete(
            f"/ng/admin/scoring/attempts/{attempt.id}",
            json={}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        db_session.refresh(score)
        assert score.points == initial_score - attempt.points

        deleted_attempt = Attempt.query.get(attempt.id)
        assert deleted_attempt is None

    def test_delete_attempt_non_admin_fails(
        self,
        logged_in_client,
        user,
        team_with_member,
        challenge,
        question,
        db_session
    ):
        """
        Test that non admin user cannot delete attempts
        """
        team_with_member.set_start_timestamp(utc_now())
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong answer",
        )
        db_session.commit()

        response = logged_in_client.delete(
            f"/ng/admin/scoring/attempts/{attempt.id}",
            json={}
        )

        assert response.status_code == 403

        still_exists = Attempt.query.get(attempt.id)
        assert still_exists is not None

    def test_delete_nonexistent_attempt(
        self,
        admin_client,
        admin
    ):
        """
        Test that deleting non existent attempt returns 404
        """
        response = admin_client.delete(
            "/ng/admin/scoring/attempts/999999",
            json={}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
