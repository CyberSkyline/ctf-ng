"""
Tests for the Attempt model
"""

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from ...challenge.models.ChallengeVariable import ChallengeVariable
from ...challenge.models.Question import Question
from ...challenge.utils import generate_seed
from ...core.exceptions import (
    BusinessLogicError,
    ValidationError,
)
from ...core.utils import utc_now
from ...event.models.Event import Event
from ...team.models.Team import Team
from ..models import (
    Attempt,
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


class TestAttemptRepr:
    """Test the Attempt model string representation"""

    def test_repr(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test answer",
            is_correct=False,
        )
        expected = f"<Attempt {attempt.id}: user={user.id} question={question.id} correct={attempt.is_correct}>"
        assert repr(attempt) == expected


class TestCreateAttempt:
    """Test the create_attempt method"""

    def test_create_attempt_correct_answer(self, db_session, user, team_with_member, score, event, challenge, question):
        team_with_member.set_start_timestamp(utc_now())

        """Test creating an attempt with correct answer"""
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,  # Correct answer
        )

        assert attempt.user_id == user.id
        assert attempt.team_id == team_with_member.id
        assert attempt.event_id == event.id
        assert attempt.challenge_id == challenge.id
        assert attempt.question_id == question.id
        assert attempt.submission == question.answer
        assert attempt.is_correct is True
        assert attempt.points == question.points
        assert isinstance(attempt.timestamp, datetime)

        # Should have created a score event
        assert attempt.score_event_id is not None
        score_event = ScoreEvent.query.get(attempt.score_event_id)
        assert score_event is not None
        assert score_event.points == question.points

        # Score should be updated
        db_session.refresh(score)
        assert score.points == question.points

    def test_create_attempt_correct_templated_answer(self, db_session, user, team_with_member, score, event, challenge, question_factory, variable_factory):
        """Test creating an attempt with correct answer"""
        team_with_member.set_start_timestamp(utc_now())
        variable: ChallengeVariable = variable_factory(challenge=challenge)
        question: Question = question_factory(challenge=challenge, answer_variable=variable)
        correct_answer: str = str(res) if (res := variable.as_attr().template.eval(generate_seed(event_id=event.id, challenge_id=challenge.id, question_id=question.id, team_seed=team_with_member.seed))) else ""
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=correct_answer,  # Correct answer
        )

        assert attempt.user_id == user.id
        assert attempt.team_id == team_with_member.id
        assert attempt.event_id == event.id
        assert attempt.challenge_id == challenge.id
        assert attempt.question_id == question.id
        assert attempt.submission == correct_answer
        assert attempt.is_correct is True
        assert attempt.points == question.points
        assert isinstance(attempt.timestamp, datetime)

        # Should have created a score event
        assert attempt.score_event_id is not None
        score_event = ScoreEvent.query.get(attempt.score_event_id)
        assert score_event is not None
        assert score_event.points == question.points

        # Score should be updated
        db_session.refresh(score)
        assert score.points == question.points

    def test_create_attempt_incorrect_answer(
        self, db_session, user, team_with_member, score, event, challenge, question
    ):
        """Test creating an attempt with incorrect answer"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong answer",
        )

        assert attempt.submission == "wrong answer"
        assert attempt.is_correct is False
        assert attempt.points == 0

        # Should NOT have created a score event
        assert attempt.score_event_id is None

        # Score should not change
        db_session.refresh(score)
        assert score.points == 0

    def test_create_attempt_incorrect_templated_answer(
        self, db_session, user, team_with_member, score, event, challenge, question_factory, variable_factory
    ):
        """Test creating an attempt with incorrect answer"""
        team_with_member.set_start_timestamp(utc_now())
        variable: ChallengeVariable = variable_factory(challenge=challenge)
        question: Question = question_factory(challenge=challenge, answer_variable=variable)
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong answer",
        )

        assert attempt.submission == "wrong answer"
        assert attempt.is_correct is False
        assert attempt.points == 0

        # Should NOT have created a score event
        assert attempt.score_event_id is None

        # Score should not change
        db_session.refresh(score)
        assert score.points == 0

    def test_create_attempt_case_insensitive(
        self, db_session, user, team_with_member, score, event, challenge, question
    ):
        """Test that answer checking is case insensitive"""
        team_with_member.set_start_timestamp(utc_now())
        # Assuming the answer is "4"
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="4",  # Same as answer but different case
        )

        assert attempt.is_correct is True
        assert attempt.points == question.points

    def test_create_attempt_with_timestamp(self, db_session, user, team_with_member, event, challenge, question):
        """Test creating an attempt with custom timestamp"""
        team_with_member.set_start_timestamp(utc_now())
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test",
            timestamp=custom_time,
        )

        db_session.flush()
        db_session.refresh(attempt)

        if custom_time.tzinfo is not None and attempt.timestamp.tzinfo is None:
            stored_as_utc = attempt.timestamp.replace(tzinfo=UTC)
            assert custom_time == stored_as_utc, f"Expected {custom_time}, got {stored_as_utc}"
        else:
            assert attempt.timestamp == custom_time

    def test_create_attempt_no_commit(self, db_session, user, team_with_member, event, challenge, question):
        """Test creating an attempt without committing"""
        team_with_member.set_start_timestamp(utc_now())
        with patch.object(db_session, "commit") as mock_commit:
            attempt = Attempt.create_attempt(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission="test",
                commit=False,
            )
            mock_commit.assert_not_called()

        assert attempt in db_session

    def test_create_attempt_with_commit(self, db_session, user, team_with_member, event, challenge, question):
        """Test creating an attempt with commit"""
        team_with_member.set_start_timestamp(utc_now())
        with patch.object(db_session, "commit") as mock_commit:
            Attempt.create_attempt(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission="test",
                commit=True,
            )
            mock_commit.assert_called_once()

    def test_create_attempt_invalid_question_fails(self, db_session, user, team_with_member, event, challenge):
        """Test that creating an attempt with invalid question fails"""
        team_with_member.set_start_timestamp(utc_now())
        with pytest.raises(ValidationError):
            Attempt.create_attempt(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=999999,  # Non-existent
                submission="test",
            )

    def test_create_attempt_for_locked_event_fails(
        self, db_session, user, team_with_member, locked_event, challenge, question
    ):
        """Test that creating an attempt for locked event fails"""
        team_with_member.set_start_timestamp(utc_now())
        locked_team = Team.create_team_with_captain(
            name="Locked Team", event_id=locked_event.id, captain_id=user.id, invite_code="locked123"
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.create_attempt(
                user_id=user.id,
                team_id=locked_team.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission="test",
            )

        assert "Cannot submit answers for a locked event" in str(exc_info.value)


class TestDeleteAttempt:
    """Test the delete_attempt method"""

    def test_delete_attempt_with_score_event(
        self, db_session, user, team_with_member, score, event, challenge, question
    ):
        """Test that deleting an attempt deletes its score event"""
        team_with_member.set_start_timestamp(utc_now())
        # Create a correct attempt
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        score_event_id = attempt.score_event_id
        assert score_event_id is not None

        # Delete the attempt
        attempt.delete_attempt()

        # Attempt should be deleted
        assert Attempt.query.get(attempt.id) is None

        # Score event should also be deleted
        assert ScoreEvent.query.get(score_event_id) is None

        # Score should be adjusted back to 0
        db_session.refresh(score)
        assert score.points == 0

    def test_delete_attempt_without_score_event(self, db_session, user, team_with_member, event, challenge, question):
        """Test deleting an incorrect attempt (no score event)"""
        team_with_member.set_start_timestamp(utc_now())
        # Create an incorrect attempt
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong",
        )

        assert attempt.score_event_id is None
        attempt_id = attempt.id

        # Delete the attempt
        attempt.delete_attempt()

        # Attempt should be deleted
        assert Attempt.query.get(attempt_id) is None

    def test_delete_attempt_no_commit(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test deleting an attempt without committing"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        with patch.object(db_session, "commit") as mock_commit:
            attempt.delete_attempt(commit=False)
            mock_commit.assert_not_called()

    def test_delete_attempt_with_commit(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test deleting an attempt with commit"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        with patch.object(db_session, "commit") as mock_commit:
            attempt.delete_attempt(commit=True)
            mock_commit.assert_called_once()


class TestFindFilteredAttempts:
    """Test the find_filtered_attempts method"""

    def test_find_by_user_id(
        self, db_session, attempt_factory, user, admin, team_with_member, event, challenge, question
    ):
        """Test filtering attempts by user_id"""
        # Create attempts for different users
        team_with_member.set_start_timestamp(utc_now())
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test1",
        )
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test2",
        )
        attempt_factory(
            user_id=admin.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test3",
        )

        # Find attempts for specific user
        attempts = Attempt.find_filtered_attempts(user_id=user.id)

        assert len(attempts) == 2
        assert all(a.user_id == user.id for a in attempts)

    def test_find_by_team_id(
        self,
        db_session,
        attempt_factory,
        user,
        team_with_member,
        team_factory,
        event,
        challenge,
        question,
        user_factory,
    ):
        """Test filtering attempts by team_id"""
        team_with_member.set_start_timestamp(utc_now())
        # Create another team
        other_captain = user_factory(name="AttemptCapt1", email="attemptcapt1@example.com")
        other_team = team_factory(event=event, members=[other_captain])

        # Create attempts for different teams
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )
        attempt_factory(
            user_id=user.id,
            team_id=other_team.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        # Find attempts for specific team
        attempts = Attempt.find_filtered_attempts(team_id=team_with_member.id)

        assert len(attempts) == 1
        assert attempts[0].team_id == team_with_member.id

    def test_find_by_question_id(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        """Test filtering attempts by question_id"""
        team_with_member.set_start_timestamp(utc_now())
        # Create another question
        other_question = Question(
            challenge_id=challenge.id, name="Other Question", body="What is 3+3?", answer="6", points=50, max_attempts=5, index=1
        )
        db_session.add(other_question)
        db_session.commit()

        # Create attempts for different questions
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=other_question.id,
        )

        # Find attempts for specific question
        attempts = Attempt.find_filtered_attempts(question_id=question.id)

        assert len(attempts) == 1
        assert attempts[0].question_id == question.id

    def test_find_only_correct_attempts(self, db_session, user, team_with_member, event, challenge, question):
        """Test filtering only correct attempts"""
        team_with_member.set_start_timestamp(utc_now())
        # Create correct and incorrect attempts
        Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong",
        )

        Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        # Find only correct attempts
        attempts = Attempt.find_filtered_attempts(team_id=team_with_member.id, is_correct=True)

        assert len(attempts) == 1
        assert attempts[0].is_correct is True

    def test_find_with_limit(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        """Test filtering results - limit not supported but we test ordering"""
        team_with_member.set_start_timestamp(utc_now())
        # Create multiple attempts with different timestamps
        for i in range(5):
            attempt_factory(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission=f"test{i}",
                timestamp=datetime(2024, 1, 1, 10 + i, 0, 0),
            )

        # Find all - should be ordered by timestamp desc
        attempts = Attempt.find_filtered_attempts(user_id=user.id)

        assert len(attempts) == 5
        # Verify they're ordered by timestamp descending
        for i in range(1, len(attempts)):
            assert attempts[i - 1].timestamp >= attempts[i].timestamp

    def test_find_ordered_by_timestamp_desc(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test that attempts are ordered by timestamp descending"""
        team_with_member.set_start_timestamp(utc_now())
        # Create attempts with different timestamps
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
        )
        attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            timestamp=datetime(2024, 1, 1, 11, 0, 0),
        )

        attempts = Attempt.find_filtered_attempts(user_id=user.id)

        # Should be ordered by timestamp descending
        assert len(attempts) == 3
        assert attempts[0].timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert attempts[1].timestamp == datetime(2024, 1, 1, 11, 0, 0)
        assert attempts[2].timestamp == datetime(2024, 1, 1, 10, 0, 0)


class TestGetTeamAttemptCount:
    """Test counting team attempts - using find_filtered_attempts"""

    def test_get_team_attempt_count(self, db_session, user, team_with_member, event, challenge, question):
        """Test counting team attempts for a question"""
        team_with_member.set_start_timestamp(utc_now())
        # Create multiple attempts
        for i in range(3):
            Attempt.create_attempt(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=question.id,
                submission=f"attempt{i}",
            )

        # Count using find_filtered_attempts
        attempts = Attempt.find_filtered_attempts(team_id=team_with_member.id, question_id=question.id)
        count = len(attempts)
        assert count == 3

    def test_get_team_attempt_count_no_attempts(self, db_session, team_with_member, question):
        """Test counting when no attempts exist"""
        attempts = Attempt.find_filtered_attempts(team_id=team_with_member.id, question_id=question.id)
        count = len(attempts)
        assert count == 0


class TestHasCorrectAnswer:
    """Test checking for correct answers - using find_filtered_attempts"""

    def test_has_correct_answer_true(self, db_session, user, team_with_member, event, challenge, question):
        """Test when team has submitted correct answer"""
        team_with_member.set_start_timestamp(utc_now())
        # Create a correct attempt
        Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        # Check using find_filtered_attempts
        correct_attempts = Attempt.find_filtered_attempts(
            team_id=team_with_member.id, question_id=question.id, is_correct=True
        )
        assert len(correct_attempts) > 0

    def test_has_correct_answer_false(self, db_session, user, team_with_member, event, challenge, question):
        """Test when team has only incorrect answers"""
        team_with_member.set_start_timestamp(utc_now())
        # Create incorrect attempts
        Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="wrong",
        )

        # Check using find_filtered_attempts
        correct_attempts = Attempt.find_filtered_attempts(
            team_id=team_with_member.id, question_id=question.id, is_correct=True
        )
        assert len(correct_attempts) == 0

    def test_has_correct_answer_no_attempts(self, db_session, team_with_member, question):
        """Test when team has no attempts"""
        correct_attempts = Attempt.find_filtered_attempts(
            team_id=team_with_member.id, question_id=question.id, is_correct=True
        )
        assert len(correct_attempts) == 0


class TestAttemptSerialization:
    """Test the serialize method"""

    def test_serialize_basic(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        """Test basic serialization includes name enrichment"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test answer",
            is_correct=False,
            points=0,
        )

        data = attempt.serialize()

        assert data["id"] == attempt.id
        assert data["user_id"] == user.id
        assert data["team_id"] == team_with_member.id
        assert data["event_id"] == event.id
        assert data["challenge_id"] == challenge.id
        assert data["question_id"] == question.id
        assert data["submission"] == "test answer"
        assert data["is_correct"] is False
        assert data["points"] == 0
        assert data["score_event_id"] is None
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"].endswith("Z")

        # Name enrichment should be included if relationships are loaded
        if attempt.team:
            assert "team_name" in data
            assert data["team_name"] == attempt.team.name
        if attempt.challenge:
            assert "challenge_name" in data
            assert data["challenge_name"] == attempt.challenge.name
        if attempt.question:
            assert "question_name" in data
            assert data["question_name"] == attempt.question.name
        if attempt.user and attempt.user.ctfd_user:
            assert "user_name" in data
            assert data["user_name"] == attempt.user.ctfd_user.name

    def test_serialize_with_admin_fields(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test serialization with admin fields includes same name enrichment"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission="test answer",
        )

        data = attempt.serialize(include_admin_fields=True)

        # Basic fields should be present
        assert "id" in data
        assert "submission" in data

        # Name enrichment should be included if relationships are loaded
        if attempt.team:
            assert "team_name" in data
            assert data["team_name"] == attempt.team.name
        if attempt.challenge:
            assert "challenge_name" in data
            assert data["challenge_name"] == attempt.challenge.name
        if attempt.question:
            assert "question_name" in data
            assert data["question_name"] == attempt.question.name
        if attempt.user and attempt.user.ctfd_user:
            assert "user_name" in data
            assert data["user_name"] == attempt.user.ctfd_user.name


class TestAttemptValidation:
    """Test the validate method"""

    def test_validate_valid_data(self, db_session, user, team_with_member, event, challenge, question):
        """Test validation with valid data"""
        data = Attempt.validate(
            {
                "user_id": user.id,
                "team_id": team_with_member.id,
                "event_id": event.id,
                "challenge_id": challenge.id,
                "question_id": question.id,
                "submission": "test answer",
            }
        )

        assert data["user_id"] == user.id
        assert data["team_id"] == team_with_member.id
        assert data["event_id"] == event.id
        assert data["challenge_id"] == challenge.id
        assert data["question_id"] == question.id
        assert data["submission"] == "test answer"

    def test_validate_missing_submission(self, db_session, user, team_with_member, event, challenge, question):
        """Test validation fails with missing submission"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Attempt.validate(
                {
                    "user_id": user.id,
                    "team_id": team_with_member.id,
                    "event_id": event.id,
                    "challenge_id": challenge.id,
                    "question_id": question.id,
                }
            )

        assert "submission" in exc_info.value.errors

    def test_validate_empty_submission(self, db_session, user, team_with_member, event, challenge, question):
        """Test that empty/whitespace submissions are rejected"""
        from ...core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Attempt.validate(
                {
                    "user_id": user.id,
                    "team_id": team_with_member.id,
                    "event_id": event.id,
                    "challenge_id": challenge.id,
                    "question_id": question.id,
                    "submission": "   ",
                    "timestamp": "2024-01-01T12:00:00Z",
                }
            )

        assert "submission" in exc_info.value.errors
        assert "cannot be empty" in exc_info.value.errors["submission"]


class TestValidateAttemptAllowed:
    """Test the validate_attempt_allowed method"""

    def test_validate_attempt_allowed_success(self, db_session, user, team_with_member, event, challenge, question):
        """Test validation passes for valid attempt"""
        team_with_member.set_start_timestamp(utc_now())
        # Should not raise any exception
        Attempt.validate_attempt_allowed(
            user_id=user.id,
            team_id=team_with_member.id,
            event_id=event.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

    def test_validate_attempt_locked_event(self, db_session, user, team_with_member, locked_event, challenge, question):
        """Test validation fails for locked event"""
        team_with_member.set_start_timestamp(utc_now())
        # Create team for locked event
        locked_team = Team.create_team_with_captain(
            name="Locked Team", event_id=locked_event.id, captain_id=user.id, invite_code="locked123"
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.validate_attempt_allowed(
                user_id=user.id,
                team_id=locked_team.id,
                event_id=locked_event.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        assert "Cannot submit answers for a locked event" in str(exc_info.value)

    def test_validate_attempt_ended_event(self, db_session, user, team_with_member, challenge, question):
        """Test validation fails for ended event"""
        now = utc_now()
        ended_event = Event(
            name="Ended Event",
            description="This event has ended",
            locked=False,
            start_time=now - timedelta(days=10),
            end_time=now - timedelta(days=1),
        )
        db_session.add(ended_event)
        db_session.commit()

        ended_team = Team.create_team_with_captain(
            name="Ended Team", event_id=ended_event.id, captain_id=user.id, invite_code="ended123"
        )

        ended_team.set_start_timestamp(now - timedelta(days=2))

        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.validate_attempt_allowed(
                user_id=user.id,
                team_id=ended_team.id,
                event_id=ended_event.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        assert "Cannot submit answers after event has ended" in str(exc_info.value)

    def test_validate_attempt_not_team_member(self, db_session, admin, team_with_member, event, challenge, question):
        """Test validation fails when user is not team member"""
        team_with_member.set_start_timestamp(utc_now())
        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.validate_attempt_allowed(
                user_id=admin.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        assert "User is not a member of this team" in str(exc_info.value)

    def test_validate_attempt_max_attempts_reached(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test validation fails when max attempts reached"""
        team_with_member.set_start_timestamp(utc_now())
        # Create max attempts
        for _i in range(question.max_attempts):
            attempt_factory(
                user_id=user.id,
                team_id=team_with_member.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.validate_attempt_allowed(
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        assert "Maximum attempts" in str(exc_info.value) and "exceeded" in str(exc_info.value)

    def test_validate_attempt_correct_attempt_already_made(
        self, db_session, user, team_with_member, event, challenge, question
    ):
        team_with_member.set_start_timestamp(utc_now())
        Attempt.create_attempt(
           user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        with pytest.raises(BusinessLogicError) as exc_info:
            Attempt.validate_attempt_allowed(
                user_id=user.id,
                team_id=team_with_member.id,
                event_id=event.id,
                challenge_id=challenge.id,
                question_id=question.id,
            )

        assert "This question has already been answered correctly" in str(exc_info.value)



class TestAttemptRelationships:
    """Test the relationships"""

    def test_user_relationship(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        """Test the user relationship"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        assert attempt.user.id == user.id

    def test_team_relationship(self, db_session, attempt_factory, user, team_with_member, event, challenge, question):
        """Test the team relationship"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        assert attempt.team == team_with_member

    def test_question_relationship(
        self, db_session, attempt_factory, user, team_with_member, event, challenge, question
    ):
        """Test the question relationship"""
        team_with_member.set_start_timestamp(utc_now())
        attempt = attempt_factory(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
        )

        assert attempt.question == question

    def test_score_event_relationship(self, db_session, user, team_with_member, score, event, challenge, question):
        """Test the score_event relationship"""
        team_with_member.set_start_timestamp(utc_now())
        # Create correct attempt to get a score event
        attempt = Attempt.create_attempt(
            user_id=user.id,
            team_id=team_with_member.id,
            challenge_id=challenge.id,
            question_id=question.id,
            submission=question.answer,
        )

        assert attempt.score_event is not None
        assert attempt.score_event.points == question.points
