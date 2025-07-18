"""
Defines the Attempt model for tracking answer submissions.
"""

from __future__ import annotations
from typing import Any, TypedDict

from datetime import datetime

from CTFd.models import db

from ... import config
from ...core.utils import utc_now
from ...core.exceptions import (
    ValidationError,
    BusinessLogicError,
)
from ...core.utils.validator import BaseValidator


class SerializedAttempt(TypedDict):
    id: int
    user_id: int
    team_id: int
    event_id: int
    challenge_id: int
    question_id: int
    score_event_id: int | None
    timestamp: str
    points: int
    submission: str
    is_correct: bool


class Attempt(db.Model):
    __tablename__ = "ng_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("ng_challenge_questions.id"), nullable=False, index=True)
    score_event_id = db.Column(db.Integer, db.ForeignKey("ng_score_events.id"), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    points = db.Column(db.Integer, nullable=False, default=0)
    submission = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.Index("ix_ng_attempts_user_question", "user_id", "question_id"),
        db.Index("ix_ng_attempts_team_question", "team_id", "question_id"),
    )

    user = db.relationship("User", backref="attempts")
    team = db.relationship("Team", backref="attempts")
    event = db.relationship("Event", backref="attempts")
    challenge = db.relationship("Challenge", backref="attempts")
    question = db.relationship("Question", backref="attempts")
    score_event = db.relationship("ScoreEvent", back_populates="attempts", uselist=False)

    def __repr__(self):
        return f"<Attempt {self.id}: user={self.user_id} question={self.question_id} correct={self.is_correct}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedAttempt:
        """
        Serialize attempt for API response
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "event_id": self.event_id,
            "challenge_id": self.challenge_id,
            "question_id": self.question_id,
            "score_event_id": self.score_event_id,
            "timestamp": self.timestamp.isoformat() + "Z" if self.timestamp else None,
            "points": self.points,
            "submission": self.submission,
            "is_correct": self.is_correct,
        }

        return SerializedAttempt(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate attempt data
        """
        validator = BaseValidator()

        validator.validate_model_id(data, "user_id", "User", required=True)
        validator.validate_model_id(data, "team_id", "Team", required=True)
        validator.validate_model_id(data, "event_id", "Event", required=True)
        validator.validate_model_id(data, "challenge_id", "Challenge", required=True)
        validator.validate_model_id(data, "question_id", "Question", required=True)

        validator.validate_string(
            data, "submission", max_length=config.MAX_SUBMISSION_LENGTH, required=True, friendly_name="Submission"
        )

        validator.validate_optional_timestamp(data)

        if "points" in data:
            try:
                points = int(data["points"])
                if points < 0:
                    validator.errors["points"] = "Points cannot be negative"
                else:
                    validator._add_parsed_data("points", points)
            except (ValueError, TypeError):
                validator.errors["points"] = "Points must be a valid integer"

        validator.validate_boolean(data, "is_correct", required=False)

        return validator.validate()

    @classmethod
    def validate_api_submission(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate answer submission from API (partial data)
        """
        validator = BaseValidator()

        validator.validate_string(
            data, "submission", config.MAX_SUBMISSION_LENGTH, required=True, friendly_name="Submission"
        )

        return validator.validate()

    @classmethod
    def validate_attempt_allowed(
        cls, user_id: int, team_id: int, event_id: int, challenge_id: int, question_id: int
    ) -> None:
        """
        Validate that an attempt is allowed
        """
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from ...challenge.models.Question import Question
        from ...event.models.Event import Event
        from ...team.models.TeamMember import TeamMember

        event = Event.find_by_id(event_id)
        if event and event.locked:
            raise BusinessLogicError("Cannot submit answers for a locked event")

        if event and event.end_time and event.end_time < utc_now().replace(tzinfo=None):
            raise BusinessLogicError("Cannot submit answers after event has ended")

        member = TeamMember.find_by_user_and_team(user_id, team_id)
        if not member:
            raise BusinessLogicError("User is not a member of this team")

        if member.event_id != event_id:
            raise BusinessLogicError("Team is not participating in this event")

        question = Question.query.get(question_id)
        if not question:
            raise ValidationError(f"Question {question_id} not found")

        if question.challenge_id != challenge_id:
            raise BusinessLogicError("This question does not belong to the specified challenge")

        existing_attempts = cls.query.filter_by(team_id=team_id, question_id=question_id).count()

        if existing_attempts >= question.max_attempts:
            raise BusinessLogicError(f"Maximum attempts ({question.max_attempts}) exceeded for this question")

    @classmethod
    def create_attempt(
        cls,
        user_id: int,
        team_id: int,
        event_id: int,
        challenge_id: int,
        question_id: int,
        submission: str,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> Attempt:
        """Create an attempt and associated score event if needed.

        Args:
            user_id: ID of the user submitting
            team_id: ID of the team
            event_id: ID of the event
            challenge_id: ID of the challenge
            question_id: ID of the question
            submission: The submitted answer
            timestamp: When submitted (defaults to now)
            commit: Whether to commit immediately

        Returns:
            Attempt: The created attempt
        """
        cls.validate_attempt_allowed(user_id, team_id, event_id, challenge_id, question_id)

        if timestamp is None:
            timestamp = utc_now()

        # LAZY-IMPORT
        from ...challenge.models.Question import Question

        question = Question.query.get(question_id)
        if not question:
            raise ValidationError(f"Question {question_id} not found")

        is_correct = submission.strip().lower() == question.answer.strip().lower()
        points = question.points if is_correct else 0

        validated_data = cls.validate(
            {
                "user_id": user_id,
                "team_id": team_id,
                "event_id": event_id,
                "challenge_id": challenge_id,
                "question_id": question_id,
                "submission": submission,
            }
        )

        attempt = cls(
            user_id=validated_data["user_id"],
            team_id=validated_data["team_id"],
            event_id=validated_data["event_id"],
            challenge_id=validated_data["challenge_id"],
            question_id=validated_data["question_id"],
            submission=validated_data["submission"],
            timestamp=timestamp,
            points=points,
            is_correct=is_correct,
        )

        db.session.add(attempt)
        db.session.flush()

        if points != 0:
            # LAZY-IMPORT
            from .Score import Score
            from .ScoreEvent import ScoreEvent

            score = Score.find_by_team_and_event(team_id, event_id)
            if score:
                score_event = ScoreEvent.create_score_event(
                    score_id=score.id, team_id=team_id, points=points, timestamp=timestamp, commit=False
                )
                attempt.score_event_id = score_event.id

        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return attempt

    @classmethod
    def find_filtered_attempts(
        cls,
        user_id: int | None = None,
        team_id: int | None = None,
        event_id: int | None = None,
        challenge_id: int | None = None,
        question_id: int | None = None,
        is_correct: bool | None = None,
    ) -> list[Attempt]:
        """
        Find attempts based on filters
        """
        query = cls.query

        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if team_id is not None:
            query = query.filter_by(team_id=team_id)
        if event_id is not None:
            query = query.filter_by(event_id=event_id)
        if challenge_id is not None:
            query = query.filter_by(challenge_id=challenge_id)
        if question_id is not None:
            query = query.filter_by(question_id=question_id)
        if is_correct is not None:
            query = query.filter_by(is_correct=is_correct)

        return query.order_by(cls.timestamp.desc()).all()

    def delete_attempt(self, commit: bool = True) -> None:
        """
        Delete this attempt and its associated score event
        """
        if self.score_event:
            self.score_event.delete_event(commit=False)

        db.session.delete(self)
        if commit:
            db.session.commit()
