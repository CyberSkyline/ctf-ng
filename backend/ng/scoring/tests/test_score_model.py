"""
Tests for the Score model
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from CTFd.cache import cache

from ...core.utils import utc_now
from ..models import Score, ScoreEvent


@pytest.fixture(autouse=True)
def clear_score_cache():
    """Clear the Redis leaderboard cache before each test"""
    from ..models import Score
    Score.clear_leaderboard_cache()
    yield
    Score.clear_leaderboard_cache()


class TestScoreRepr:
    """Test the Score model string representation"""

    def test_repr(self, score):
        expected = f"<Score {score.id}: team={score.team_id} event={score.event_id} points={score.points}>"
        assert repr(score) == expected


class TestCreateScore:
    """Test the create_score method"""

    def test_create_score_defaults(self, db_session, team_with_member, event):
        # Check if score already exists from team creation
        existing = Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).first()

        if existing:
            # Test the existing score
            score = existing
        else:
            # Create a new score
            score = Score.create_score(team_id=team_with_member.id)

        assert score.team_id == team_with_member.id
        assert score.event_id == event.id
        assert score.points == 0
        assert score.team_name == team_with_member.name
        assert isinstance(score.last_update, datetime)

        # Verify it's persisted
        found_score = Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).first()
        assert found_score is not None
        assert found_score.id == score.id

    def test_create_score_no_commit(self, db_session, team_factory, event_factory, user_factory):
        # Create a new team and event to ensure no score exists
        new_event = event_factory()
        # Create a user to be the team captain
        captain = user_factory(name="Captain1", email="captain1@example.com")
        new_team = team_factory(event=new_event, members=[captain])

        # Delete the auto-created score to test creation
        existing = Score.query.filter_by(team_id=new_team.id, event_id=new_event.id).first()
        if existing:
            db_session.delete(existing)
            db_session.commit()

        with patch.object(db_session, "commit") as mock_commit:
            score = Score.create_score(team_id=new_team.id, commit=False)
            mock_commit.assert_not_called()

        # Should still be in session
        assert score in db_session

    def test_create_score_with_commit(self, db_session, team_factory, event_factory, user_factory):
        # Create a new team and event to ensure no score exists
        new_event = event_factory()
        # Create a user to be the team captain
        captain = user_factory(name="Captain2", email="captain2@example.com")
        new_team = team_factory(event=new_event, members=[captain])

        # Delete the auto-created score to test creation
        existing = Score.query.filter_by(team_id=new_team.id, event_id=new_event.id).first()
        if existing:
            db_session.delete(existing)
            db_session.commit()

        with patch.object(db_session, "commit") as mock_commit:
            Score.create_score(team_id=new_team.id, commit=True)
            mock_commit.assert_called_once()

    def test_create_duplicate_score_raises_error(self, db_session, score):
        """Test that creating a duplicate score for same team/event raises error"""
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            Score.create_score(team_id=score.team_id)


class TestScoreAdjust:
    """Test the adjust method"""

    def test_adjust_positive(self, db_session, score):
        original_points = score.points
        score.adjust(100)

        assert score.points == original_points + 100
        assert score.last_update is not None

        # Verify persistence
        db_session.refresh(score)
        assert score.points == original_points + 100

    def test_adjust_negative(self, db_session, score):
        score.points = 200  # Start with some points
        db_session.commit()

        score.adjust(-50)
        assert score.points == 150

        db_session.refresh(score)
        assert score.points == 150

    def test_adjust_no_commit(self, db_session, score):
        with patch.object(db_session, "commit") as mock_commit:
            score.adjust(100, commit=False)
            mock_commit.assert_not_called()

        assert score.points == 100

    def test_adjust_with_commit(self, db_session, score):
        with patch.object(db_session, "commit") as mock_commit:
            score.adjust(100, commit=True)
            mock_commit.assert_called_once()

        assert score.points == 100

class TestScoreMarkCorrectSubmission:
    """Test the mark_correct_submission method"""

    def test_mark_correct_submission(self, db_session, score, team_with_member, question, user):
        from ..models.Attempt import Attempt

        team_with_member.set_start_timestamp(utc_now())

        new_attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=question.challenge_id,
            question_id=question.id,
            submission=question.answer,  # Correct answer
        )

        score.mark_correct_submission(timestamp=new_attempt.timestamp)

        delta = new_attempt.timestamp.replace(tzinfo=None) - team_with_member.start_timestamp.replace(tzinfo=None)
        offset = delta / timedelta(milliseconds=1)
        assert offset == score.last_correct_offset

class TestScoreRecalculate:
    """Test the recalculate method"""

    def test_recalculate_empty(self, db_session, score):
        """Test recalculating with no score events"""
        score.points = 999  # Set to non-zero
        db_session.commit()

        score.recalculate()

        assert score.points == 0
        assert score.last_correct_offset == 0
        db_session.refresh(score)
        assert score.points == 0
        assert score.last_correct_offset == 0

    def test_recalculate_with_events(self, db_session, score, team_with_member, question, user, score_event_factory):
        """Test recalculating with multiple score events"""
        team_with_member.set_start_timestamp(utc_now())

        # Create several score events
        score_event_factory(score_id=score.id, team_id=score.team_id, points=100)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=-20)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=50)

        # Create a correct attempt
        from ..models.Attempt import Attempt

        new_attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=question.challenge_id,
            question_id=question.id,
            submission=question.answer,  # Correct answer
        )

        # Set score to wrong value
        score.points = 999
        score.last_correct_offset = 0
        db_session.commit()

        # Recalculate
        score.recalculate()

        delta = new_attempt.timestamp.replace(tzinfo=None) - team_with_member.start_timestamp.replace(tzinfo=None)
        offset = delta / timedelta(milliseconds=1)

        # Should be sum of events: 100 - 20 + 50 = 130
        assert score.points == 130 + question.points
        assert score.last_correct_offset == offset
        db_session.refresh(score)
        assert score.points == 130 + question.points
        assert score.last_correct_offset == offset

    def test_recalculate_no_commit(self, db_session, score, score_event_factory):
        score_event_factory(score_id=score.id, team_id=score.team_id, points=100)

        with patch.object(db_session, "commit") as mock_commit:
            score.recalculate(commit=False)
            mock_commit.assert_not_called()

        assert score.points == 100

    def test_recalculate_with_commit(self, db_session, score, score_event_factory):
        score_event_factory(score_id=score.id, team_id=score.team_id, points=100)

        with patch.object(db_session, "commit") as mock_commit:
            score.recalculate(commit=True)
            mock_commit.assert_called_once()

        assert score.points == 100


class TestGetLeaderboard:
    """Test the get_leaderboard class method"""

    def test_get_leaderboard_empty(self, db_session, event):
        """Test leaderboard for event with no scores"""
        leaderboard = Score.get_leaderboard(event.id)

        assert leaderboard == []

    def test_get_leaderboard_ordering(self, db_session, event_factory, team_factory, user_factory):
        """Test leaderboard returns teams in descending score order"""
        cache.clear()

        # Create a fresh event and teams to avoid cache issues
        fresh_event = event_factory()

        # Create teams and update their auto-created scores
        teams_and_scores = []
        for i in range(3):
            captain = user_factory(name=f"Captain{i}", email=f"captain{i}@example.com")
            team = team_factory(event=fresh_event, members=[captain])
            team.set_start_timestamp(utc_now())
            # Get the auto-created score
            score = Score.query.filter_by(team_id=team.id, event_id=fresh_event.id).first()
            score.points = (i + 1) * 100
            db_session.commit()
            teams_and_scores.append((team, score))

        # Verify scores are in database before calling get_leaderboard
        db_scores = Score.query.filter_by(event_id=fresh_event.id).all()
        assert len(db_scores) == 3, f"Expected 3 scores in DB, found {len(db_scores)}"

        # Get leaderboard
        leaderboard = Score.get_leaderboard(fresh_event.id)

        assert len(leaderboard) == 3, f"Expected 3 in leaderboard, got {len(leaderboard)}"

        # Check ordering - should be 300, 200, 100
        assert leaderboard[0]["points"] == 300
        assert leaderboard[1]["points"] == 200
        assert leaderboard[2]["points"] == 100

    def test_get_leaderboard_caching(self, db_session, event_factory, team_factory, user_factory):
        """Test that leaderboard is cached"""

        cache.clear()

        fresh_event = event_factory()

        # Create initial team and update its score
        captain1 = user_factory(name="CacheCaptain1", email="cachec1@example.com")
        team1 = team_factory(event=fresh_event, members=[captain1])
        team1.set_start_timestamp(utc_now())
        score1 = Score.query.filter_by(team_id=team1.id, event_id=fresh_event.id).first()
        score1.points = 100
        db_session.commit()

        # Get leaderboard - should cache
        leaderboard1 = Score.get_leaderboard(fresh_event.id)
        assert len(leaderboard1) == 1

        # Add another team and update its score
        captain2 = user_factory(name="CacheCaptain2", email="cachec2@example.com")
        team2 = team_factory(event=fresh_event, members=[captain2])
        team2.set_start_timestamp(utc_now())
        score2 = Score.query.filter_by(team_id=team2.id, event_id=fresh_event.id).first()
        score2.points = 200
        db_session.commit()

        # Get leaderboard again - should return cached version
        leaderboard2 = Score.get_leaderboard(fresh_event.id)
        assert len(leaderboard2) == 1  # Still cached

        # Clear both CTFd cache and Redis leaderboard cache and get again
        cache.clear()
        from ..models import Score
        Score.clear_leaderboard_cache(event_id=fresh_event.id)
        leaderboard3 = Score.get_leaderboard(fresh_event.id)
        assert len(leaderboard3) == 2  # Now shows both teams

    def test_get_leaderboard_with_tied_scores(self, db_session, event_factory, team_factory, user_factory):
        """Test leaderboard handles tied scores correctly"""
        cache.clear()

        fresh_event = event_factory()

        # Create teams and update their scores
        captain1 = user_factory(name="TiedCaptain1", email="tiedc1@example.com")
        team1 = team_factory(event=fresh_event, members=[captain1])
        team1.set_start_timestamp(utc_now())
        captain2 = user_factory(name="TiedCaptain2", email="tiedc2@example.com")
        team2 = team_factory(event=fresh_event, members=[captain2])
        team2.set_start_timestamp(utc_now())
        captain3 = user_factory(name="TiedCaptain3", email="tiedc3@example.com")
        team3 = team_factory(event=fresh_event, members=[captain3])
        team3.set_start_timestamp(utc_now())
        # Update auto-created scores
        score1 = Score.query.filter_by(team_id=team1.id, event_id=fresh_event.id).first()
        score1.points = 100
        score1.last_update = datetime(2024, 1, 1, 10, 0, 0)

        score2 = Score.query.filter_by(team_id=team2.id, event_id=fresh_event.id).first()
        score2.points = 100
        score2.last_update = datetime(2024, 1, 1, 11, 0, 0)  # Later update

        score3 = Score.query.filter_by(team_id=team3.id, event_id=fresh_event.id).first()
        score3.points = 50

        db_session.commit()

        leaderboard = Score.get_leaderboard(fresh_event.id)

        # Check we have 3 teams
        assert len(leaderboard) == 3

        # First two should have 100 points, last should have 50
        assert leaderboard[0]["points"] == 100
        assert leaderboard[1]["points"] == 100
        assert leaderboard[2]["points"] == 50


class TestGetTeamRank:
    """Test the get_team_rank class method"""

    def test_get_team_rank(self, db_session, event, multiple_teams_with_scores):
        """Test getting rank for specific teams"""
        teams_data = multiple_teams_with_scores

        # Test ranks for each team
        for i, team_data in enumerate(teams_data):
            rank = Score.get_team_rank(team_data["team"].id)
            # Team 4 has highest score (500), so rank 1
            # Team 0 has lowest score (100), so rank 5
            expected_rank = 5 - i
            assert rank == expected_rank

    def test_get_team_rank_nonexistent(self, db_session, event):
        """Test rank for team that doesn't exist in event"""
        rank = Score.get_team_rank(999999)
        assert rank is None

    def test_get_team_rank_uses_cache(self, db_session, event, score):
        """Test that get_team_rank uses cached leaderboard"""
        # Populate cache
        Score.get_leaderboard(event.id)

        # Get rank without mocking to ensure it works
        rank = Score.get_team_rank(score.team_id)
        assert rank == 1  # Only team, so rank 1


class TestScoreSerialization:
    """Test the serialize method"""

    def test_serialize_basic(self, score):
        data = score.serialize()

        assert data["id"] == score.id
        assert data["team_id"] == score.team_id
        assert data["event_id"] == score.event_id
        assert data["points"] == score.points
        assert data["team_name"] == score.team_name
        assert "last_update" in data
        assert isinstance(data["last_update"], str)
