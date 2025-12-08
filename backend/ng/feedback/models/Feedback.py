"""
Defines the Feedback model for user feedback
"""

from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import db
from sqlalchemy import JSON

from ...core.utils import utc_now
from ...core.exceptions import ValidationError
from ...core.utils.validator import BaseValidator



class SerializedFeedback(TypedDict):
    id: int
    user_id: int
    event_id: int
    challenge_id: int | None
    feedback_data: dict[str, Any]
    created_at: str
    updated_at: str


class Feedback(db.Model):
    __tablename__ = "ng_feedback"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_users.id"),
        nullable = False,
        index = True
    )
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_events.id"),
        nullable = False,
        index = True
    )
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_challenges.id"),
        nullable = True,
        index = True
    )
    feedback_data = db.Column(JSON, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable = False,
        default = utc_now,
        onupdate = utc_now
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "event_id",
            "challenge_id",
            name = "uq_feedback_user_event_challenge"
        ),
        db.CheckConstraint(
            "(challenge_id IS NULL) OR (challenge_id IS NOT NULL AND event_id IS NOT NULL)",
            name = "ck_feedback_requires_event"
        ),
    )

    user = db.relationship("User")
    event = db.relationship("Event")
    challenge = db.relationship("Challenge")

    def __repr__(self) -> str:
        return f"<Feedback {self.id} user={self.user_id} event={self.event_id} challenge={self.challenge_id}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedFeedback:
        """
        Serialize feedback for API response
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "challenge_id": self.challenge_id,
            "feedback_data": self.feedback_data,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate feedback data
        """
        validator = BaseValidator()

        validator.validate_model_id(data, "user_id", "User", required = True)
        validator.validate_model_id(data, "event_id", "Event", required = True)
        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required = False
        )

        if "feedback_data" not in data or not isinstance(data["feedback_data"],
                                                         dict):
            validator.errors["feedback_data"
                             ] = "Feedback data must be a valid object"

        validated_data = validator.validate()
        validated_data["feedback_data"] = data.get("feedback_data", {})

        return validated_data

    @classmethod
    def create_feedback(
        cls,
        user_id: int,
        event_id: int,
        feedback_data: dict[str, Any],
        *,
        challenge_id: int | None = None,
        commit: bool = True,
    ) -> Feedback:
        validated_data = cls.validate(
            {
                "user_id": user_id,
                "event_id": event_id,
                "challenge_id": challenge_id,
                "feedback_data": feedback_data,
            }
        )

        feedback = cls(
            user_id = validated_data["user_id"],
            event_id = validated_data["event_id"],
            challenge_id = validated_data.get("challenge_id"),
            feedback_data = validated_data["feedback_data"],
        )

        db.session.add(feedback)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        return feedback

    def update_feedback(
        self,
        feedback_data: dict[str,
                            Any],
        commit: bool = True
    ) -> None:
        if not isinstance(feedback_data, dict):
            raise ValidationError("Feedback data must be a dictionary")

        self.feedback_data = feedback_data
        self.updated_at = utc_now()
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, feedback_id: int) -> Feedback | None:
        return cls.query.get(feedback_id)

    @classmethod
    def find_filtered_feedback(
        cls,
        user_id: int | None = None,
        event_id: int | None = None,
        challenge_id: int | None = None,
    ) -> list[Feedback]:
        query = cls.query

        if user_id is not None:
            query = query.filter_by(user_id = user_id)
        if event_id is not None:
            query = query.filter_by(event_id = event_id)
        if challenge_id is not None:
            query = query.filter_by(challenge_id = challenge_id)

        return query.order_by(cls.updated_at.desc()).all()
