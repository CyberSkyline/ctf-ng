"""
Tests for scoring controllers
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from ...core.exceptions import (
    BusinessLogicError,
    NotFoundError,
    ValidationError,
)
from ..controllers import (
    submit_answer,
    redeem_hint,
    get_leaderboard,
    get_team_score,
    award_manual_points,
    get_score_history,
    recalculate_score,
)
from ..models import (
    Attempt,
    HintRedemption,
    ManualPointAward,
    Score,
    ScoreEvent,
)


@pytest.fixture(autouse=True)
def clear_score_cache():
    """Clear the memoize cache before each test"""
    from ...core.utils.cache import _cache

    _cache.clear()
    yield
    _cache.clear()


class TestSubmitAnswer:
    """Test the submit_answer controller"""

    def test_submit_answer_correct(self, db_session, user, team_with_member, event, challenge, question, score):
        """Test submitting a correct answer"""
        result = submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )

        assert result["is_correct"] is True
        assert result["points_awarded"] == question.points
        assert result["new_score"] == question.points

        # Verify attempt was created
        attempt = Attempt.query.filter_by(user_id=user.id, question_id=question.id).first()
        assert attempt is not None
        assert attempt.is_correct is True
        assert attempt.points == question.points

    def test_submit_answer_incorrect(self, db_session, user, team_with_member, event, challenge, question, score):
        """Test submitting an incorrect answer"""
        result = submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong answer",
            current_user_id=user.id,
        )

        assert result["is_correct"] is False
        assert result["points_awarded"] == 0
        assert result["new_score"] == 0

        # Verify attempt was created
        attempt = Attempt.query.filter_by(user_id=user.id, question_id=question.id).first()
        assert attempt is not None
        assert attempt.is_correct is False
        assert attempt.points == 0

    def test_submit_answer_user_not_in_team(self, db_session, admin, event, challenge, question):
        """Test submitting answer when user is not in a team"""
        with pytest.raises(BusinessLogicError) as exc_info:
            submit_answer(
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission="test",
                current_user_id=admin.id,
            )

        assert "must be part of a team" in str(exc_info.value)

    def test_submit_answer_team_not_found(self, db_session, user, event, challenge, question):
        """Test submitting answer when team is not found"""
        with pytest.raises(BusinessLogicError) as exc_info:
            submit_answer(
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission="test",
                current_user_id=user.id,
            )

        assert "must be part of a team" in str(exc_info.value)

    def test_submit_answer_with_existing_score(
        self, db_session, user, team_with_member, event, challenge, question, score
    ):
        """Test submitting answer when score exists and gets updated"""
        # Set initial score
        score.points = 50
        db_session.commit()

        result = submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )

        expected_new_score = 50 + question.points
        assert result["new_score"] == expected_new_score

        # Verify score was updated
        db_session.refresh(score)
        assert score.points == expected_new_score

    def test_submit_answer_no_score_record(self, db_session, user, team_with_member, event, challenge, question):
        """Test submitting answer when no score record exists"""
        # Delete any existing score
        Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).delete()
        db_session.commit()

        result = submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )

        assert result["new_score"] == 0  # No score record found


class TestRedeemHint:
    """Test the redeem_hint controller"""

    def test_redeem_hint_success(self, db_session, user, team_with_member, event, challenge, hint):
        """Test successfully redeeming a hint"""
        result = redeem_hint(
            event_id=event.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            current_user_id=user.id,
        )

        assert "redemption" in result
        assert result["hint_body"] == hint.body
        assert result["points_deducted"] == hint.deduction

        # Verify redemption was created
        redemption = HintRedemption.query.filter_by(user_id=user.id, hint_id=hint.id).first()
        assert redemption is not None
        assert redemption.points == -hint.deduction

    def test_redeem_hint_user_not_in_team(self, db_session, admin, event, challenge, hint):
        """Test redeeming hint when user is not in a team"""
        with pytest.raises(BusinessLogicError) as exc_info:
            redeem_hint(
                event_id=event.id,
                challenge_id=challenge.id,
                hint_id=hint.id,
                current_user_id=admin.id,
            )

        assert "must be part of a team" in str(exc_info.value)

    def test_redeem_hint_already_redeemed(self, db_session, user, team_with_member, event, challenge, hint):
        """Test redeeming hint that was already redeemed"""
        # Create initial redemption
        HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=event.id,
            challenge_id=challenge.id,
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            redeem_hint(
                event_id=event.id,
                challenge_id=challenge.id,
                hint_id=hint.id,
                current_user_id=user.id,
            )

        assert "already been redeemed" in str(exc_info.value)

    def test_redeem_hint_zero_deduction(self, db_session, user, team_with_member, event, challenge):
        """Test redeeming hint with zero deduction"""
        from ...challenge.models.Hint import Hint

        # Create hint with zero deduction
        free_hint = Hint(challenge_id=challenge.id, preview="Free hint", body="This is a free hint", deduction=0)
        db_session.add(free_hint)
        db_session.commit()

        result = redeem_hint(
            event_id=event.id,
            challenge_id=challenge.id,
            hint_id=free_hint.id,
            current_user_id=user.id,
        )

        assert result["points_deducted"] == 0
        assert result["hint_body"] == free_hint.body


class TestGetLeaderboard:
    """Test the get_leaderboard controller"""

    def test_get_leaderboard_empty(self, db_session, event):
        """Test getting leaderboard for event with no teams"""
        result = get_leaderboard(event.id)

        assert result == []

    def test_get_leaderboard_with_teams(self, db_session, event, multiple_teams_with_scores):
        """Test getting leaderboard with multiple teams"""
        result = get_leaderboard(event.id)

        assert len(result) == 5
        # Should be ordered by points descending
        assert result[0]["points"] >= result[1]["points"]
        assert result[1]["points"] >= result[2]["points"]

    def test_get_leaderboard_with_limit(self, db_session, event, multiple_teams_with_scores):
        """Test getting leaderboard with limit"""
        result = get_leaderboard(event.id, limit=3)

        assert len(result) == 3
        # Should be top 3 teams
        assert result[0]["points"] >= result[1]["points"]
        assert result[1]["points"] >= result[2]["points"]

    def test_get_leaderboard_default_limit(self, db_session, event, multiple_teams_with_scores):
        """Test getting leaderboard with default limit"""
        result = get_leaderboard(event.id)

        # Should return all teams (5 in this case)
        assert len(result) == 5


class TestGetTeamScore:
    """Test the get_team_score controller"""

    def test_get_team_score_basic(self, db_session, event, team_with_member, score):
        """Test getting basic team score"""
        result = get_team_score(event.id, team_with_member.id)

        assert "score" in result
        assert "rank" in result
        assert result["score"] == score
        assert result["rank"] == 1  # Only team

    def test_get_team_score_with_history(self, db_session, event, team_with_member, score, score_event):
        """Test getting team score with history"""
        result = get_team_score(event.id, team_with_member.id, include_history=True)

        assert "score" in result
        assert "rank" in result
        assert "recent_events" in result
        assert len(result["recent_events"]) >= 1

    def test_get_team_score_not_found(self, db_session, event, team_with_member):
        """Test getting score for team that doesn't exist in event"""
        # Delete the score
        Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).delete()
        db_session.commit()

        with pytest.raises(NotFoundError) as exc_info:
            get_team_score(event.id, team_with_member.id)

        assert "No score found" in str(exc_info.value)

    def test_get_team_score_rank_calculation(self, db_session, event, multiple_teams_with_scores):
        """Test that rank is calculated correctly"""
        teams_data = multiple_teams_with_scores

        # Get score for the team with lowest points (index 0 = 100 points)
        lowest_team = teams_data[0]["team"]
        result = get_team_score(event.id, lowest_team.id)

        assert result["rank"] == 5  # Should be last place


class TestAwardManualPoints:
    """Test the award_manual_points controller"""

    def test_award_manual_points_positive(self, db_session, admin, event, team_with_member, score):
        """Test awarding positive manual points"""
        initial_points = score.points

        result = award_manual_points(
            event_id=event.id,
            team_id=team_with_member.id,
            points=100,
            reason="Excellent teamwork",
            admin_id=admin.id,
        )

        assert "award" in result
        assert "updated_score" in result
        assert result["previous_points"] == initial_points
        assert result["new_points"] == initial_points + 100

        # Verify award was created
        award = ManualPointAward.query.filter_by(team_id=team_with_member.id, admin_id=admin.id).first()
        assert award is not None
        assert award.points == 100
        assert award.reason == "Excellent teamwork"

    def test_award_manual_points_negative(self, db_session, admin, event, team_with_member, score):
        """Test awarding negative manual points (penalty)"""
        score.points = 200
        db_session.commit()

        result = award_manual_points(
            event_id=event.id,
            team_id=team_with_member.id,
            points=-50,
            reason="Rule violation",
            admin_id=admin.id,
        )

        assert result["previous_points"] == 200
        assert result["new_points"] == 150

        # Verify award was created with negative points
        award = ManualPointAward.query.filter_by(team_id=team_with_member.id, admin_id=admin.id).first()
        assert award is not None
        assert award.points == -50

    def test_award_manual_points_team_not_found(self, db_session, admin, event, team_with_member):
        """Test awarding points to team with no score"""
        # Delete the score
        Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).delete()
        db_session.commit()

        with pytest.raises(NotFoundError) as exc_info:
            award_manual_points(
                event_id=event.id,
                team_id=team_with_member.id,
                points=100,
                reason="Test",
                admin_id=admin.id,
            )

        assert "has no score in event" in str(exc_info.value)

    def test_award_manual_points_zero_points_fails(self, db_session, admin, event, team_with_member, score):
        """Test that awarding zero points fails"""
        with pytest.raises(ValidationError) as exc_info:
            award_manual_points(
                event_id=event.id,
                team_id=team_with_member.id,
                points=0,
                reason="Test",
                admin_id=admin.id,
            )

        assert "cannot be zero" in str(exc_info.value.errors.get("points", ""))

    def test_award_manual_points_non_admin_fails(self, db_session, user, event, team_with_member, score):
        """Test that non-admin cannot award points"""
        with pytest.raises(ValidationError) as exc_info:
            award_manual_points(
                event_id=event.id,
                team_id=team_with_member.id,
                points=100,
                reason="Test",
                admin_id=user.id,
            )

        assert "must be an admin" in str(exc_info.value.errors.get("admin_id", ""))


class TestGetScoreHistory:
    """Test the get_score_history controller"""

    def test_get_score_history_basic(self, db_session, event, score_event):
        """Test getting basic score history"""
        result = get_score_history(event.id)

        assert "total_events" in result
        assert "events" in result
        assert "filters_applied" in result
        assert result["total_events"] >= 1
        assert len(result["events"]) >= 1

    def test_get_score_history_with_team_filter(self, db_session, event, team_with_member, score_event):
        """Test getting score history filtered by team"""
        result = get_score_history(event.id, team_id=team_with_member.id)

        assert result["filters_applied"]["team_id"] == team_with_member.id
        assert all(event.team_id == team_with_member.id for event in result["events"])

    def test_get_score_history_with_limit(self, db_session, event, score_event_factory, score):
        """Test getting score history with limit"""
        # Create multiple score events
        for i in range(10):
            score_event_factory(score_id=score.id, team_id=score.team_id, points=10 * (i + 1))

        result = get_score_history(event.id, limit=5)

        assert len(result["events"]) == 5
        assert result["filters_applied"]["limit"] == 5

    def test_get_score_history_eager_loading(self, db_session, event, score_event):
        """Test that eager loading is enabled for score history"""
        with patch.object(ScoreEvent, "find_filtered_events") as mock_find:
            mock_find.return_value = [score_event]

            get_score_history(event.id)

            mock_find.assert_called_once()
            call_args = mock_find.call_args
            assert call_args[1]["eager_load_source"] is True

    def test_get_score_history_empty(self, db_session, event):
        """Test getting score history for event with no events"""
        result = get_score_history(event.id)

        assert result["total_events"] == 0
        assert result["events"] == []


class TestRecalculateScore:
    """Test the recalculate_score controller"""

    def test_recalculate_score_basic(self, db_session, event, team_with_member, score):
        """Test basic score recalculation"""
        # Manually set score to wrong value
        score.points = 999
        db_session.commit()

        result = recalculate_score(event.id, team_with_member.id)

        assert result["team_id"] == team_with_member.id
        assert result["event_id"] == event.id
        assert result["old_points"] == 999
        assert result["new_points"] == 0  # No score events
        assert result["difference"] == -999

    def test_recalculate_score_with_events(self, db_session, event, team_with_member, score, score_event_factory):
        """Test score recalculation with score events"""
        # Create score events
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=100)
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=50)
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=-20)

        # Manually set score to wrong value
        score.points = 999
        db_session.commit()

        result = recalculate_score(event.id, team_with_member.id)

        assert result["old_points"] == 999
        assert result["new_points"] == 130  # 100 + 50 - 20
        assert result["difference"] == -869

    def test_recalculate_score_not_found(self, db_session, event, team_with_member):
        """Test recalculating score for team that doesn't exist in event"""
        # Delete the score
        Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).delete()
        db_session.commit()

        with pytest.raises(NotFoundError) as exc_info:
            recalculate_score(event.id, team_with_member.id)

        assert "has no score in event" in str(exc_info.value)

    def test_recalculate_score_updates_timestamp(self, db_session, event, team_with_member, score):
        """Test that recalculation updates the last_update timestamp"""
        old_timestamp = score.last_update

        result = recalculate_score(event.id, team_with_member.id)

        assert "last_update" in result
        # Timestamp should be updated
        db_session.refresh(score)
        assert score.last_update > old_timestamp

    def test_recalculate_score_no_change(self, db_session, event, team_with_member, score):
        """Test recalculating score when no change is needed"""
        # Score is already correct (0 points, no events)
        result = recalculate_score(event.id, team_with_member.id)

        assert result["old_points"] == 0
        assert result["new_points"] == 0
        assert result["difference"] == 0


class TestControllerIntegration:
    """Integration tests for multiple controllers working together"""

    def test_complete_scoring_flow(
        self, db_session, user, team_with_member, event, challenge, question, hint, admin, score
    ):
        """Test complete flow: submit answer, redeem hint, award points"""
        initial_score = score.points

        # 1. Submit correct answer
        answer_result = submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )
        assert answer_result["is_correct"] is True

        # 2. Redeem hint
        hint_result = redeem_hint(
            event_id=event.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            current_user_id=user.id,
        )
        assert hint_result["points_deducted"] == hint.deduction

        # 3. Award manual points
        award_manual_points(
            event_id=event.id,
            team_id=team_with_member.id,
            points=50,
            reason="Bonus points",
            admin_id=admin.id,
        )

        # 4. Check final score
        final_score = get_team_score(event.id, team_with_member.id)
        expected_total = initial_score + question.points - hint.deduction + 50
        assert final_score["score"].points == expected_total

        # 5. Check leaderboard
        leaderboard = get_leaderboard(event.id)
        assert len(leaderboard) >= 1
        assert leaderboard[0]["points"] == expected_total

    def test_score_history_reflects_all_actions(
        self, db_session, user, team_with_member, event, challenge, question, hint, admin, score
    ):
        """Test that score history shows all scoring actions"""
        # Perform various actions
        submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )

        redeem_hint(
            event_id=event.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            current_user_id=user.id,
        )

        award_manual_points(
            event_id=event.id,
            team_id=team_with_member.id,
            points=25,
            reason="Good sportsmanship",
            admin_id=admin.id,
        )

        # Check history
        history = get_score_history(event.id, team_id=team_with_member.id)

        # Should have 3 events (answer, hint, manual award)
        assert history["total_events"] == 3

        # Events should be ordered by timestamp descending
        events = history["events"]
        assert len(events) == 3

        # Verify point values
        total_points = sum(event.points for event in events)
        expected_total = question.points - hint.deduction + 25
        assert total_points == expected_total

    def test_recalculate_after_complex_scoring(
        self, db_session, user, team_with_member, event, challenge, question, hint, admin, score
    ):
        """Test recalculation after complex scoring operations"""
        # Perform multiple scoring actions
        submit_answer(
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
            current_user_id=user.id,
        )

        redeem_hint(
            event_id=event.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            current_user_id=user.id,
        )

        award_manual_points(
            event_id=event.id,
            team_id=team_with_member.id,
            points=30,
            reason="Creativity bonus",
            admin_id=admin.id,
        )

        # Get current score
        current_score = score.points

        # Recalculate should show no difference
        recalc_result = recalculate_score(event.id, team_with_member.id)

        assert recalc_result["old_points"] == current_score
        assert recalc_result["new_points"] == current_score
        assert recalc_result["difference"] == 0
