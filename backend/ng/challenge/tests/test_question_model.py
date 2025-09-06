"""
Test cases for the Question model to verify validation and database operations.
"""

import base64
import os

import pytest

from ...core.exceptions import ValidationError
from ..models import Challenge
from ..models.Question import Question
from ... import config


@pytest.fixture
def valid_question_data(challenge):
    """Valid question data for testing."""
    return {
        "name": "Test Question",
        "body": "What is the answer to this test question?",
        "points": 100,
        "answer": "test_answer",
        "max_attempts": 3,
        "challenge_id": challenge.id,
    }


class Test_Question_Validate:
    """Test validation logic for Question model."""

    def test_validate_with_valid_data_should_pass(self, valid_question_data):
        """Test that validation passes with valid data."""
        validated_data = Question.validate(valid_question_data)

        assert validated_data["name"] == valid_question_data["name"]
        assert validated_data["body"] == valid_question_data["body"]
        assert validated_data["points"] == valid_question_data["points"]
        assert validated_data["answer"] == valid_question_data["answer"]
        assert validated_data["max_attempts"] == valid_question_data["max_attempts"]
        assert validated_data["challenge_id"] == valid_question_data["challenge_id"]

    def test_validate_missing_name_should_fail(self, valid_question_data):
        """Test that validation fails when name is missing."""
        del valid_question_data["name"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Name" in str(exc_info.value.errors)

    def test_validate_empty_name_should_fail(self, valid_question_data):
        """Test that validation fails when name is empty."""
        valid_question_data["name"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Name" in str(exc_info.value.errors)

    def test_validate_name_too_long_should_fail(self, valid_question_data):
        """Test that validation fails when name exceeds maximum length."""
        valid_question_data["name"] = "a" * (config.MAX_QUESTION_NAME_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Name" in str(exc_info.value.errors)

    def test_validate_missing_body_should_fail(self, valid_question_data):
        """Test that validation fails when body is missing."""
        del valid_question_data["body"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Body" in str(exc_info.value.errors)

    def test_validate_empty_body_should_fail(self, valid_question_data):
        """Test that validation fails when body is empty."""
        valid_question_data["body"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Body" in str(exc_info.value.errors)

    def test_validate_body_too_long_should_fail(self, valid_question_data):
        """Test that validation fails when body exceeds maximum length."""
        valid_question_data["body"] = "a" * (config.MAX_QUESTION_BODY_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Question Body" in str(exc_info.value.errors)

    def test_validate_missing_points_should_fail(self, valid_question_data):
        """Test that validation fails when points is missing."""
        del valid_question_data["points"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Points" in str(exc_info.value.errors)

    def test_validate_negative_points_should_fail(self, valid_question_data):
        """Test that validation fails when points is negative."""
        valid_question_data["points"] = -1

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Points" in str(exc_info.value.errors)

    def test_validate_zero_points_should_fail(self, valid_question_data):
        """Test that validation fails when points is zero."""
        valid_question_data["points"] = 0

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Points" in str(exc_info.value.errors)

    def test_validate_missing_answer_should_fail(self, valid_question_data):
        """Test that validation fails when answer is missing."""
        del valid_question_data["answer"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Answer" in str(exc_info.value.errors)

    def test_validate_empty_answer_should_fail(self, valid_question_data):
        """Test that validation fails when answer is empty."""
        valid_question_data["answer"] = ""

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Answer" in str(exc_info.value.errors)

    def test_validate_answer_too_long_should_fail(self, valid_question_data):
        """Test that validation fails when answer exceeds maximum length."""
        valid_question_data["answer"] = "a" * (config.MAX_QUESTION_ANSWER_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Answer" in str(exc_info.value.errors)

    def test_validate_missing_max_attempts_should_fail(self, valid_question_data):
        """Test that validation fails when max_attempts is missing."""
        del valid_question_data["max_attempts"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Max Attempts" in str(exc_info.value.errors)

    def test_validate_negative_max_attempts_should_fail(self, valid_question_data):
        """Test that validation fails when max_attempts is negative."""
        valid_question_data["max_attempts"] = -1

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Max Attempts" in str(exc_info.value.errors)

    def test_validate_zero_max_attempts_should_fail(self, valid_question_data):
        """Test that validation fails when max_attempts is zero."""
        valid_question_data["max_attempts"] = 0

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Max Attempts" in str(exc_info.value.errors)

    def test_validate_missing_challenge_id_should_fail(self, valid_question_data):
        """Test that validation fails when challenge_id is missing."""
        del valid_question_data["challenge_id"]

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_negative_challenge_id_should_fail(self, valid_question_data):
        """Test that validation fails when challenge_id is negative."""
        valid_question_data["challenge_id"] = -1

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Challenge ID" in str(exc_info.value.errors)

    def test_validate_zero_challenge_id_should_fail(self, valid_question_data):
        """Test that validation fails when challenge_id is zero."""
        valid_question_data["challenge_id"] = 0

        with pytest.raises(ValidationError) as exc_info:
            Question.validate(valid_question_data)

        assert "Challenge ID" in str(exc_info.value.errors)


@pytest.mark.db
class Test_Create_Question:
    """Test database operations for Question model."""

    def test_create_question_with_valid_data_should_succeed(self, db_session, valid_question_data):
        """Test that creating a question with valid data succeeds."""
        question = Question.create_question(**valid_question_data)

        assert question.id is not None
        assert question.name == valid_question_data["name"]
        assert question.body == valid_question_data["body"]
        assert question.points == valid_question_data["points"]
        assert question.answer == valid_question_data["answer"]
        assert question.max_attempts == valid_question_data["max_attempts"]
        assert question.challenge_id == valid_question_data["challenge_id"]

    def test_create_question_should_persist_to_database(self, db_session, valid_question_data):
        """Test that created question is properly persisted to database."""
        question = Question.create_question(**valid_question_data)

        # Retrieve from database
        retrieved_question = Question.query.get(question.id)

        assert retrieved_question is not None
        assert retrieved_question.name == valid_question_data["name"]
        assert retrieved_question.body == valid_question_data["body"]
        assert retrieved_question.points == valid_question_data["points"]
        assert retrieved_question.answer == valid_question_data["answer"]
        assert retrieved_question.max_attempts == valid_question_data["max_attempts"]
        assert retrieved_question.challenge_id == valid_question_data["challenge_id"]

    def test_create_question_with_invalid_data_should_fail(self, db_session, challenge):
        """Test that creating a question with invalid data fails."""
        invalid_data = {
            "name": "",  # Invalid: empty name
            "body": "Test body",
            "points": 100,
            "answer": "test_answer",
            "max_attempts": 3,
            "challenge_id": challenge.id,
        }

        with pytest.raises(ValidationError):
            Question.create_question(**invalid_data)

    def test_create_question_should_rollback_on_validation_error(self, db_session, challenge):
        """Test that database rollback occurs when validation fails."""
        initial_count = Question.query.count()

        invalid_data = {
            "name": "",  # Invalid: empty name
            "body": "Test body",
            "points": 100,
            "answer": "test_answer",
            "max_attempts": 3,
            "challenge_id": challenge.id,
        }

        with pytest.raises(ValidationError):
            Question.create_question(**invalid_data)

        # Verify no question was created
        assert Question.query.count() == initial_count

    def test_create_question_with_commit_false_should_not_commit(self, db_session, valid_question_data):
        """Test that creating a question with commit=False doesn't commit to database."""
        question = Question.create_question(commit=False, **valid_question_data)

        # Flush session to clear it
        db_session.flush()
        db_session.expunge_all()

        # Question should exist in session but not committed
        assert question.id is not None

        # After rollback, question should not exist
        db_session.rollback()
        retrieved_question = Question.query.get(question.id)
        assert retrieved_question is None

    def test_question_challenge_relationship_should_work(self, db_session, valid_question_data, challenge):
        """Test that the relationship between Question and Challenge works."""
        question = Question.create_question(**valid_question_data)

        # Test that question has reference to challenge
        assert question.challenge is not None
        assert question.challenge.id == challenge.id
        assert question.challenge.name == challenge.name

    def test_create_multiple_questions_for_same_challenge(self, db_session, challenge):
        """Test that multiple questions can be created for the same challenge."""
        question1_data = {
            "name": "Question 1",
            "body": "First question body",
            "points": 100,
            "answer": "answer1",
            "max_attempts": 3,
            "challenge_id": challenge.id,
        }

        question2_data = {
            "name": "Question 2",
            "body": "Second question body",
            "points": 200,
            "answer": "answer2",
            "max_attempts": 5,
            "challenge_id": challenge.id,
        }

        question1 = Question.create_question(**question1_data)
        question2 = Question.create_question(**question2_data)

        assert question1.id != question2.id
        assert question1.challenge_id == question2.challenge_id == challenge.id

        # Both questions should be retrievable
        assert Question.query.get(question1.id) is not None
        assert Question.query.get(question2.id) is not None


class Test_Check_Answer:
    def test_check_answer_with_correct_answer(self, db_session, admin_client, event, team_factory,user):
        team = team_factory(event=event, members=[user]) # noqa F841

        with open(os.path.join(os.path.dirname(__file__), "./yamls/default.yaml"), "rb") as f:
            yaml = base64.urlsafe_b64encode(f.read())

        admin_client.post("/ng/admin/challenge/import", json={"yaml": yaml.decode("utf-8")})

        # challenge = Challenge.query.filter_by(name="Basic Challenge").first()
        # question = Question.query.filter_by(name="Q1").first()

        # question.check_answer(team, "CTF{test_flag}")

        # print(challenge)
        # print(question)
        # print(team)
        # raise Exception("test")
