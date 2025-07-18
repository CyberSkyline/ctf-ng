"""
Tests for the ScoreEvent model
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from ..models.ScoreEvent import ScoreEvent
from ..models.Score import Score


@pytest.fixture(autouse=True)
def clear_score_cache():
    """Clear the memoize cache before each test"""
    from ...core.utils.cache import _cache

    _cache.clear()
    yield
    _cache.clear()


class TestScoreEventRepr:
    """Test the ScoreEvent model string representation"""

    def test_repr(self, score_event):
        expected = f"<ScoreEvent {score_event.id}: team={score_event.team_id} points={score_event.points}>"
        assert repr(score_event) == expected


class TestCreateScoreEvent:
    """Test the create_score_event method"""

    def test_create_score_event_defaults(self, db_session, score):
        """Test creating a score event with default values"""
        try:
            event = ScoreEvent.create_score_event(score_id=score.id, team_id=score.team_id, points=50)
        except Exception as e:
            if hasattr(e, "errors"):
                print(f"Validation errors: {e.errors}")
            raise

        assert event.score_id == score.id
        assert event.team_id == score.team_id
        assert event.points == 50
        assert isinstance(event.timestamp, datetime)

        # Verify it's persisted
        found_event = ScoreEvent.query.filter_by(id=event.id).first()
        assert found_event is not None

        # Verify score was adjusted
        db_session.refresh(score)
        assert score.points == 50

    def test_create_score_event_negative_points(self, db_session, score):
        """Test creating a score event with negative points"""
        # Set initial points
        score.points = 100
        db_session.commit()

        event = ScoreEvent.create_score_event(score_id=score.id, team_id=score.team_id, points=-30)

        assert event.points == -30

        # Verify score was adjusted
        db_session.refresh(score)
        assert score.points == 70

    def test_create_score_event_with_timestamp(self, db_session, score):
        """Test creating a score event with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)

        event = ScoreEvent.create_score_event(
            score_id=score.id, team_id=score.team_id, points=100, timestamp=custom_time
        )

        assert event.timestamp == custom_time

    def test_create_score_event_no_commit(self, db_session, score):
        """Test creating a score event without committing"""
        with patch.object(db_session, "commit") as mock_commit:
            event = ScoreEvent.create_score_event(score_id=score.id, team_id=score.team_id, points=100, commit=False)
            mock_commit.assert_not_called()

        # Should still be in session
        assert event in db_session

    def test_create_score_event_with_commit(self, db_session, score):
        """Test creating a score event with commit"""
        with patch.object(db_session, "commit") as mock_commit:
            ScoreEvent.create_score_event(score_id=score.id, team_id=score.team_id, points=100, commit=True)
            mock_commit.assert_called_once()

    def test_create_score_event_zero_points_fails(self, db_session, score):
        """Test that creating a score event with zero points fails validation"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.create_score_event(score_id=score.id, team_id=score.team_id, points=0)

        assert "points" in exc_info.value.errors
        assert "Points cannot be zero" in exc_info.value.errors["points"]

    def test_create_score_event_invalid_score_id_fails(self, db_session, team_with_member):
        """Test that creating a score event with invalid score_id fails"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            ScoreEvent.create_score_event(
                score_id=999999,  # Non-existent
                team_id=team_with_member.id,
                points=100,
            )

    def test_create_score_event_invalid_team_id_fails(self, db_session, score):
        """Test that creating a score event with invalid team_id fails"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            ScoreEvent.create_score_event(
                score_id=score.id,
                team_id=999999,  # Non-existent
                points=100,
            )


class TestDeleteEvent:
    """Test the delete_event method"""

    def test_delete_event_adjusts_score(self, db_session, score, score_event):
        """Test that deleting an event reverses the score adjustment"""
        # Initial state: score has 50 points from fixture
        assert score.points == 50

        # Delete the event
        score_event.delete_event()

        # Score should be back to 0
        db_session.refresh(score)
        assert score.points == 0

        # Event should be deleted
        assert ScoreEvent.query.filter_by(id=score_event.id).first() is None

    def test_delete_event_no_commit(self, db_session, score_event, score):
        """Test deleting an event without committing"""
        # Mock both the session commit and the score's adjust method to control commits
        with patch.object(db_session, "commit") as mock_commit:
            with patch.object(score, "adjust") as mock_adjust:
                score_event.delete_event(commit=False)
                mock_commit.assert_not_called()
                # Verify adjust was called with the negative points and commit=False
                mock_adjust.assert_called_once_with(-score_event.points, commit=False)

    def test_delete_event_with_commit(self, db_session, score_event, score):
        """Test deleting an event with commit"""
        with patch.object(db_session, "commit") as mock_commit:
            # Mock score.adjust to prevent it from calling commit
            with patch.object(score, "adjust") as mock_adjust:
                score_event.delete_event(commit=True)
                # Should be called once by delete_event
                mock_commit.assert_called_once()
                mock_adjust.assert_called_once_with(-score_event.points, commit=True)

    def test_delete_event_does_not_delete_source_records(self, db_session, score, team_with_member, question, user):
        """Test that deleting a score event does NOT delete source records (Attempts, etc)"""
        from ..models.Attempt import Attempt

        # Create an attempt with the correct answer - this should create a score event
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=score.event_id,
            challenge_id=question.challenge_id,
            question_id=question.id,
            submission=question.answer,  # Correct answer
        )

        # Verify the attempt was marked as correct and has points
        assert attempt.is_correct is True
        assert attempt.points == question.points

        # Get the created score event
        score_event = ScoreEvent.query.filter_by(
            score_id=score.id, team_id=team_with_member.id, points=question.points
        ).first()

        assert score_event is not None
        assert attempt.score_event_id == score_event.id

        # Store attempt ID before deletion
        attempt_id = attempt.id

        # Delete the score event
        score_event.delete_event()

        # Attempt should still exist but score_event_id should be null
        from ..models.Attempt import Attempt as AttemptModel

        attempt_after = AttemptModel.query.get(attempt_id)
        assert attempt_after is not None  # Attempt should NOT be deleted
        assert attempt_after.score_event_id is None  # But reference should be cleared


class TestFindFilteredEvents:
    """Test the find_filtered_events method"""

    def test_find_by_score_id(self, db_session, score, score_event_factory, team_factory, event):
        """Test filtering events by score_id"""
        # Create multiple events
        score_event_factory(score_id=score.id, team_id=score.team_id, points=10)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=20)

        # Create a different team and score for comparison
        other_team = team_factory(event=event)
        # Score already created automatically when team was created
        other_score = Score.query.filter_by(team_id=other_team.id, event_id=event.id).first()
        score_event_factory(score_id=other_score.id, team_id=other_team.id, points=30)

        # Find events for specific score
        events = ScoreEvent.find_filtered_events(score_id=score.id)

        # Should only find events for the first score
        assert len(events) == 2  # Only the 2 we created for this score
        assert all(e.score_id == score.id for e in events)

    def test_find_by_team_id(self, db_session, score, score_event, score_event_factory, team_factory, event):
        """Test filtering events by team_id"""
        # Create events for same team (in addition to fixture)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=10)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=20)

        # Create event for different team
        other_team = team_factory(event=event)
        # Score already created automatically when team was created
        other_score = Score.query.filter_by(team_id=other_team.id, event_id=event.id).first()
        score_event_factory(score_id=other_score.id, team_id=other_team.id, points=30)

        # Find events for specific team
        events = ScoreEvent.find_filtered_events(team_id=score.team_id)

        assert len(events) == 3  # Original fixture + 2 new ones
        assert all(e.team_id == score.team_id for e in events)

    def test_find_by_event_id(
        self, db_session, score, score_event, score_event_factory, event_factory, team_factory, team_with_member
    ):
        """Test filtering events by event_id"""
        # Create events for same event (in addition to fixture)
        score_event_factory(score_id=score.id, team_id=score.team_id, points=10)

        # Create score and event for different event
        other_event = event_factory()
        # Need to create a team in the other event to get a score
        other_team = team_factory(event=other_event)
        other_score = Score.query.filter_by(team_id=other_team.id, event_id=other_event.id).first()
        score_event_factory(score_id=other_score.id, team_id=other_team.id, points=20)

        # Find events for specific event
        events = ScoreEvent.find_filtered_events(event_id=score.event_id)

        assert len(events) == 2  # Original fixture + 1 new one
        assert all(e.score.event_id == score.event_id for e in events)

    def test_find_with_limit(self, db_session, score, score_event_factory):
        """Test limiting results"""
        # Create multiple events
        for i in range(5):
            score_event_factory(score_id=score.id, team_id=score.team_id, points=(i + 1) * 10)

        # Find with limit
        events = ScoreEvent.find_filtered_events(score_id=score.id, limit=3)

        assert len(events) == 3

    def test_find_events_ordered_by_timestamp_desc(self, db_session, score, score_event_factory):
        """Test that events are ordered by timestamp descending"""
        # Clear any existing events to have predictable results
        ScoreEvent.query.filter_by(score_id=score.id).delete()
        db_session.commit()

        # Create events with different timestamps
        score_event_factory(
            score_id=score.id, team_id=score.team_id, points=10, timestamp=datetime(2024, 1, 1, 10, 0, 0)
        )
        score_event_factory(
            score_id=score.id, team_id=score.team_id, points=20, timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
        score_event_factory(
            score_id=score.id, team_id=score.team_id, points=30, timestamp=datetime(2024, 1, 1, 11, 0, 0)
        )

        events = ScoreEvent.find_filtered_events(score_id=score.id)

        # Should be ordered by timestamp descending (newest first)
        assert len(events) == 3
        assert events[0].points == 20  # 12:00
        assert events[1].points == 30  # 11:00
        assert events[2].points == 10  # 10:00


class TestScoreEventSerialization:
    """Test the serialize method"""

    def test_serialize_basic(self, score_event):
        """Test basic serialization"""
        data = score_event.serialize()

        assert data["id"] == score_event.id
        assert data["score_id"] == score_event.score_id
        assert data["team_id"] == score_event.team_id
        assert data["points"] == score_event.points
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

    def test_serialize_with_admin_fields(self, score_event):
        """Test serialization with admin fields (currently same as basic)"""
        data = score_event.serialize(include_admin_fields=True)

        # Currently no additional admin fields, but structure is there
        assert data["id"] == score_event.id
        assert data["score_id"] == score_event.score_id
        assert data["team_id"] == score_event.team_id
        assert data["points"] == score_event.points
        assert "timestamp" in data


class TestScoreEventValidation:
    """Test the validate method"""

    def test_validate_valid_data(self, db_session, score):
        """Test validation with valid data"""
        # Validate without timestamp (it's optional)
        data = ScoreEvent.validate({"score_id": score.id, "team_id": score.team_id, "points": 100})

        assert data["score_id"] == score.id
        assert data["team_id"] == score.team_id
        assert data["points"] == 100

    def test_validate_with_timestamp_string(self, db_session, score):
        """Test validation with timestamp as ISO string"""
        from ...core.utils import utc_now

        timestamp = utc_now()

        # The validator expects the timezone info to be in the string already
        # utc_now() returns a datetime with tzinfo=UTC
        data = ScoreEvent.validate(
            {
                "score_id": score.id,
                "team_id": score.team_id,
                "points": 100,
                "timestamp": timestamp.isoformat(),  # This already includes timezone info
            }
        )

        assert data["score_id"] == score.id
        assert data["team_id"] == score.team_id
        assert data["points"] == 100
        assert "timestamp" in data
        assert isinstance(data["timestamp"], datetime)

    def test_validate_missing_score_id(self, db_session, team_with_member):
        """Test validation fails with missing score_id"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.validate({"team_id": team_with_member.id, "points": 100})

        assert "score_id" in exc_info.value.errors

    def test_validate_missing_team_id(self, db_session, score):
        """Test validation fails with missing team_id"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.validate({"score_id": score.id, "points": 100})

        assert "team_id" in exc_info.value.errors

    def test_validate_missing_points(self, db_session, score):
        """Test validation fails with missing points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.validate({"score_id": score.id, "team_id": score.team_id})

        assert "points" in exc_info.value.errors
        assert "Points value is required" in exc_info.value.errors["points"]

    def test_validate_zero_points(self, db_session, score):
        """Test validation fails with zero points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.validate({"score_id": score.id, "team_id": score.team_id, "points": 0})

        assert "points" in exc_info.value.errors
        assert "Points cannot be zero" in exc_info.value.errors["points"]

    def test_validate_non_integer_points(self, db_session, score):
        """Test validation fails with non-integer points"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScoreEvent.validate(
                {
                    "score_id": score.id,
                    "team_id": score.team_id,
                    "points": "100",
                }
            )

        assert "points" in exc_info.value.errors
        assert "Points must be an integer" in exc_info.value.errors["points"]


class TestScoreEventRelationships:
    """Test the relationships"""

    def test_score_relationship(self, score_event, score):
        """Test the score relationship"""
        assert score_event.score == score
        assert score_event in score.events

    def test_team_relationship(self, score_event, team_with_member):
        """Test the team relationship"""
        assert score_event.team == team_with_member
        assert score_event in team_with_member.score_events
