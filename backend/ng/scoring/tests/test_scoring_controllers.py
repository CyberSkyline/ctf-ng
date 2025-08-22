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
    get_team_attempts,
    get_team_hint_redemptions,
    get_team_manual_awards,
)
from ..models import (
    Attempt,
    HintRedemption,
    ManualPointAward,
    Score,
    ScoreEvent,
)
from ...challenge.models.Hint import Hint


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
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )

        # Result is now an Attempt object
        assert isinstance(result, Attempt)
        assert result.is_correct is True
        assert result.points == question.points
        assert result.submission == question.answer

        # Verify the score was updated
        db_session.refresh(score)
        assert score.points == question.points

    def test_submit_answer_incorrect(self, db_session, user, team_with_member, event, challenge, question, score):
        """Test submitting an incorrect answer"""
        result = submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission="wrong answer",
        )

        # Result is now an Attempt object
        assert isinstance(result, Attempt)
        assert result.is_correct is False
        assert result.points == 0
        assert result.submission == "wrong answer"

        # Verify the score was not updated
        db_session.refresh(score)
        assert score.points == 0

    def test_submit_answer_with_existing_score(
        self, db_session, user, team_with_member, event, challenge, question, score
    ):
        """Test submitting answer when score exists and gets updated"""
        # Set initial score
        score.points = 50
        db_session.commit()

        result = submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )

        # Result is the Attempt object
        assert isinstance(result, Attempt)
        assert result.is_correct is True
        assert result.points == question.points

        # Verify score was updated
        expected_new_score = 50 + question.points
        db_session.refresh(score)
        assert score.points == expected_new_score

    def test_submit_answer_no_score_record(self, db_session, user, team_with_member, event, challenge, question):
        """Test submitting answer when no score record exists"""
        # Delete any existing score
        Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).delete()
        db_session.commit()

        result = submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )

        # Result is the Attempt object
        assert isinstance(result, Attempt)
        assert result.is_correct is True
        assert result.points == question.points

        # Verify score was created (by Score.find_by_team_and_event)
        score = Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).first()
        assert score is not None
        assert score.points == question.points


class TestRedeemHint:
    """Test the redeem_hint controller"""

    def test_redeem_hint_success(self, db_session, user, team_with_member, event, challenge, hint):
        """Test successfully redeeming a hint"""
        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )

        # Result is now a serialized hint with body revealed
        assert isinstance(result, dict)
        assert result["id"] == hint.id
        assert result["body"] == hint.body  # Body should be revealed
        assert result["preview"] == hint.preview
        assert result["is_redeemed"] is True
        assert result["deduction"] == hint.deduction

        # Verify redemption was created in database
        redemption = HintRedemption.find_by_team_and_hint(team_with_member.id, hint.id)
        assert redemption is not None
        assert redemption.points == -hint.deduction

    def test_redeem_hint_already_redeemed(self, db_session, user, team_with_member, event, challenge, hint):
        """Test redeeming hint that was already redeemed"""
        # Create initial redemption
        HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            redeem_hint(
                event=event,
                challenge=challenge,
                hint=hint,
                team=team_with_member,
                current_user=user,
            )

        assert "already been redeemed" in str(exc_info.value)

    def test_redeem_hint_zero_deduction(self, db_session, user, team_with_member, event, challenge):
        """Test redeeming hint with zero deduction"""
        # Create hint with zero deduction
        free_hint = Hint(challenge_id=challenge.id, preview="Free hint", body="This is a free hint", deduction=0)
        db_session.add(free_hint)
        db_session.commit()

        result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=free_hint,
            team=team_with_member,
            current_user=user,
        )

        # Result is a serialized hint
        assert isinstance(result, dict)
        assert result["body"] == "This is a free hint"  # Body revealed
        assert result["is_redeemed"] is True
        assert result["deduction"] == 0

        # Verify redemption was created with zero points
        redemption = HintRedemption.find_by_team_and_hint(team_with_member.id, free_hint.id)
        assert redemption is not None
        assert redemption.points == 0  # No deduction for free hint


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
        result = get_team_score(score=score)

        # Controller now just returns the score object
        assert isinstance(result, Score)
        assert result.team_id == team_with_member.id
        assert result.event_id == event.id
        assert result.points == score.points


class TestAwardManualPoints:
    """Test the award_manual_points controller"""

    def test_award_manual_points_positive(self, db_session, admin, event, team_with_member, score):
        """Test awarding positive manual points"""
        initial_points = score.points

        result = award_manual_points(
            event=event,
            team=team_with_member,
            score=score,
            points=100,
            reason="Excellent teamwork",
            admin_id=admin.id,
        )

        # Result is now a ManualPointAward object
        assert isinstance(result, ManualPointAward)
        assert result.team_id == team_with_member.id
        assert result.admin_id == admin.id
        assert result.points == 100
        assert result.reason == "Excellent teamwork"

        # Verify score was updated
        db_session.refresh(score)
        assert score.points == initial_points + 100

    def test_award_manual_points_negative(self, db_session, admin, event, team_with_member, score):
        """Test awarding negative manual points (penalty)"""
        score.points = 200
        db_session.commit()

        result = award_manual_points(
            event=event,
            team=team_with_member,
            score=score,
            points=-50,
            reason="Rule violation",
            admin_id=admin.id,
        )

        # Result is a ManualPointAward object
        assert isinstance(result, ManualPointAward)
        assert result.points == -50

        # Verify score was updated
        db_session.refresh(score)
        assert score.points == 150

        # Verify award was created with negative points
        award = ManualPointAward.query.filter_by(team_id=team_with_member.id, admin_id=admin.id).first()
        assert award is not None
        assert award.points == -50

    def test_award_manual_points_zero_points_fails(self, db_session, admin, event, team_with_member, score):
        """Test that awarding zero points fails"""
        with pytest.raises(ValidationError) as exc_info:
            award_manual_points(
                event=event,
                team=team_with_member,
                score=score,
                points=0,
                reason="Test",
                admin_id=admin.id,
            )

        assert "cannot be zero" in str(exc_info.value.errors.get("points", ""))

    def test_award_manual_points_non_admin_fails(self, db_session, user, event, team_with_member, score):
        """Test that non-admin cannot award points"""
        with pytest.raises(ValidationError) as exc_info:
            award_manual_points(
                event=event,
                team=team_with_member,
                score=score,
                points=100,
                reason="Test",
                admin_id=user.id,
            )

        assert "must be an admin" in str(exc_info.value.errors.get("admin_id", ""))


class TestGetScoreHistory:
    """Test the get_score_history controller"""

    def test_get_score_history_basic(self, db_session, event, team_with_member, score_event):
        """Test getting basic score history"""
        result = get_score_history(event, team_with_member)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(isinstance(se, ScoreEvent) for se in result)

    def test_get_score_history_with_team_filter(self, db_session, event, team_with_member, score_event):
        """Test getting score history filtered by team"""
        result = get_score_history(event, team_with_member)

        # All events should be for the specified team
        assert all(se.team_id == team_with_member.id for se in result)

    def test_get_score_history_with_limit(self, db_session, event, team_with_member, score_event_factory, score):
        """Test getting score history with limit"""
        # Create multiple score events
        for i in range(10):
            score_event_factory(score_id=score.id, team_id=score.team_id, points=10 * (i + 1))

        result = get_score_history(event, team_with_member, limit=5)

        # Should return only 5 events
        assert len(result) == 5

    def test_get_score_history_eager_loading(self, db_session, event, team_with_member, score_event):
        """Test that eager loading is enabled for score history"""
        with patch.object(ScoreEvent, "find_filtered_events") as mock_find:
            mock_find.return_value = [score_event]

            get_score_history(event, team_with_member)

            mock_find.assert_called_once()
            call_args = mock_find.call_args
            assert call_args[1]["eager_load_source"] is True

    def test_get_score_history_empty(self, db_session, event, team_with_member):
        """Test getting score history for event with no events"""
        result = get_score_history(event, team_with_member)

        # Should return empty list
        assert result == []


class TestRecalculateScore:
    """Test the recalculate_score controller"""

    def test_recalculate_score_basic(self, db_session, event, team_with_member, score):
        """Test basic score recalculation"""
        # Manually set score to wrong value
        old_points = 999
        score.points = old_points
        db_session.commit()

        result = recalculate_score(score)

        # Result is the updated Score object
        assert isinstance(result, Score)
        assert result.team_id == team_with_member.id
        assert result.event_id == event.id
        assert result.points == 0  # No score events, so should be 0

    def test_recalculate_score_with_events(self, db_session, event, team_with_member, score, score_event_factory):
        """Test score recalculation with score events"""
        # Create score events
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=100)
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=50)
        score_event_factory(score_id=score.id, team_id=team_with_member.id, points=-20)

        # Manually set score to wrong value
        score.points = 999
        db_session.commit()

        result = recalculate_score(score)

        # Result is the updated Score object
        assert isinstance(result, Score)
        assert result.points == 130  # 100 + 50 - 20

    def test_recalculate_score_updates_timestamp(self, db_session, event, team_with_member, score):
        """Test that recalculation updates the last_update timestamp"""
        old_timestamp = score.last_update

        recalculate_score(score)

        db_session.refresh(score)
        assert score.last_update > old_timestamp

    def test_recalculate_score_no_change(self, db_session, event, team_with_member, score):
        """Test recalculating score when no change is needed"""
        # Score is already correct (0 points, no events)
        result = recalculate_score(score)

        assert result.points == 0  # Should remain 0


class TestControllerIntegration:
    """Integration tests for multiple controllers working together"""

    def test_complete_scoring_flow(
        self, db_session, user, team_with_member, event, challenge, question, hint, admin, score
    ):
        """Test complete flow: submit answer, redeem hint, award points"""
        initial_score = score.points

        # 1. Submit correct answer
        answer_result = submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )
        assert answer_result.is_correct is True

        # 2. Redeem hint
        hint_result = redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )
        # Hint result is now a serialized hint
        assert hint_result["is_redeemed"] is True
        assert hint_result["body"] == hint.body

        # Verify the hint redemption created the deduction
        redemption = HintRedemption.find_by_team_and_hint(team_with_member.id, hint.id)
        assert redemption.points == -hint.deduction

        # 3. Award manual points
        award_result = award_manual_points(
            event=event,
            team=team_with_member,
            score=score,
            points=50,
            reason="Bonus points",
            admin_id=admin.id,
        )
        assert award_result.points == 50

        # 4. Check final score
        db_session.refresh(score)
        expected_total = initial_score + question.points - hint.deduction + 50
        assert score.points == expected_total

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
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )

        redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )

        award_manual_points(
            event=event,
            team=team_with_member,
            score=score,
            points=25,
            reason="Good sportsmanship",
            admin_id=admin.id,
        )

        # Check history
        history = get_score_history(event, team_with_member)

        # Should have 3 events (answer, hint, manual award)
        assert len(history) == 3

        # Events should be ScoreEvent objects
        assert all(isinstance(se, ScoreEvent) for se in history)

        # Verify point values
        total_points = sum(se.points for se in history)
        expected_total = question.points - hint.deduction + 25
        assert total_points == expected_total

    def test_recalculate_after_complex_scoring(
        self, db_session, user, team_with_member, event, challenge, question, hint, admin, score
    ):
        """Test recalculation after complex scoring operations"""
        # Perform multiple scoring actions
        submit_answer(
            event=event,
            challenge=challenge,
            question=question,
            team=team_with_member,
            current_user=user,
            submission=question.answer,
        )

        redeem_hint(
            event=event,
            challenge=challenge,
            hint=hint,
            team=team_with_member,
            current_user=user,
        )

        award_manual_points(
            event=event,
            team=team_with_member,
            score=score,
            points=30,
            reason="Creativity bonus",
            admin_id=admin.id,
        )

        # Get current score
        db_session.refresh(score)
        current_score = score.points

        # Recalculate should show no difference
        recalc_result = recalculate_score(score)

        # Score should remain the same since it was already correct
        assert recalc_result.points == current_score


class TestGetTeamAttempts:
    """Test the get_team_attempts controller"""

    def test_get_team_attempts_empty(self, db_session, event, team_with_member):
        """Test getting attempts for team with no attempts"""
        result = get_team_attempts(team_id=team_with_member.id, event_id=event.id)
        assert result == []

    def test_get_team_attempts_with_data(self, db_session, event, team_with_member, user, challenge, question):
        """Test getting attempts for team with attempts (including failed ones)"""
        # Create a correct attempt
        correct_attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        # Create a failed attempt
        failed_attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong answer",
        )

        result = get_team_attempts(team_id=team_with_member.id, event_id=event.id)

        assert len(result) >= 2
        assert all(isinstance(attempt, Attempt) for attempt in result)

        # Find our specific attempts
        correct_attempt_found = any(a.id == correct_attempt.id for a in result)
        failed_attempt_found = any(a.id == failed_attempt.id for a in result)

        assert correct_attempt_found, "Should find correct attempt"
        assert failed_attempt_found, "Should find failed attempt"


class TestGetTeamHintRedemptions:
    """Test the get_team_hint_redemptions controller"""

    def test_get_team_hint_redemptions_empty(self, db_session, event, team_with_member):
        """Test getting hint redemptions for team with no redemptions"""
        result = get_team_hint_redemptions(team_id=team_with_member.id, event_id=event.id)
        assert result == []

    def test_get_team_hint_redemptions_with_data(self, db_session, event, team_with_member, user, challenge, hint):
        """Test getting hint redemptions for team with redemptions"""
        # Create a hint redemption
        redemption = HintRedemption.create_redemption(
            hint_id=hint.id,
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
        )

        result = get_team_hint_redemptions(team_id=team_with_member.id, event_id=event.id)

        assert len(result) >= 1
        assert all(isinstance(r, HintRedemption) for r in result)

        # Find our specific redemption
        redemption_found = any(r.id == redemption.id for r in result)
        assert redemption_found, "Should find hint redemption"


class TestGetTeamManualAwards:
    """Test the get_team_manual_awards controller"""

    def test_get_team_manual_awards_empty(self, db_session, event, team_with_member):
        """Test getting manual awards for team with no awards"""
        result = get_team_manual_awards(team_id=team_with_member.id, event_id=event.id)
        assert result == []

    def test_get_team_manual_awards_with_data(self, db_session, event, team_with_member, admin):
        """Test getting manual awards for team with awards"""
        # Create a manual award
        award = ManualPointAward.create_award(
            admin_id=admin.id,
            team_id=team_with_member.id,
            points=50,
            reason="Test bonus"
        )

        result = get_team_manual_awards(team_id=team_with_member.id, event_id=event.id)

        assert len(result) >= 1
        assert all(isinstance(a, ManualPointAward) for a in result)

        # Find our specific award
        award_found = any(a.id == award.id for a in result)
        assert award_found, "Should find manual award"
