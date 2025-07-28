"""
Defines the HintRedemption model for tracking hint usage.
"""

from __future__ import annotations
from typing import Any, TypedDict

from datetime import datetime

from CTFd.models import db

from ...core.utils import utc_now
from ...core.exceptions import (
    ValidationError,
    BusinessLogicError,
)
from ...core.utils.validator import BaseValidator


class SerializedHintRedemption(TypedDict):
    id: int
    hint_id: int
    user_id: int
    team_id: int
    score_event_id: int | None
    timestamp: str
    points: int


class HintRedemption(db.Model):
    __tablename__ = "ng_hint_redemptions"

    id = db.Column(db.Integer, primary_key=True)
    hint_id = db.Column(db.Integer, db.ForeignKey("ng_challenge_hints.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    score_event_id = db.Column(db.Integer, db.ForeignKey("ng_score_events.id"), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    points = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("team_id", "hint_id", name="uq_hint_redemption_team_hint"),
        db.Index("ix_ng_hint_redemptions_team", "team_id"),
    )

    hint = db.relationship("Hint", backref="redemptions")
    user = db.relationship("User", backref="hint_redemptions")
    team = db.relationship("Team", backref="hint_redemptions")
    score_event = db.relationship("ScoreEvent", back_populates="hint_redemptions", uselist=False)

    def __repr__(self):
        return f"<HintRedemption {self.id}: team={self.team_id} hint={self.hint_id}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedHintRedemption:
        """
        Serialize hint redemption for API response
        """
        data = {
            "id": self.id,
            "hint_id": self.hint_id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "score_event_id": self.score_event_id,
            "timestamp": self.timestamp.isoformat() + "Z",
            "points": self.points,
        }

        return SerializedHintRedemption(**data)  # type: ignore[typeddict-item, no-any-return]

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate hint redemption data.
        """
        validator = BaseValidator()

        validator.validate_model_id(data, "hint_id", "Hint", required=True)
        validator.validate_model_id(data, "user_id", "User", required=True)
        validator.validate_model_id(data, "team_id", "Team", required=True)

        validator.validate_datetime(data, "timestamp", required=False)

        return validator.validate()  # type: ignore[no-any-return]

    @classmethod
    def validate_redemption_allowed(
        cls, user_id: int, team_id: int, hint_id: int, event_id: int, challenge_id: int
    ) -> None:
        """
        Validate that a hint redemption is allowed for the user in the given event.
        """
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from ...challenge.models.Hint import Hint
        from ...team.models.TeamMember import TeamMember
        from ...event.models.Event import Event

        # TODO: Move most logic to permission check system
        member = TeamMember.find_by_user_and_team(user_id, team_id)
        if not member:
            raise BusinessLogicError("User is not a member of this team.")

        if member.event_id != event_id:
            raise BusinessLogicError("This hint is not valid for the event you are currently in.")

        event = Event.query.get(event_id)
        if event and event.locked:
            raise BusinessLogicError("Cannot redeem hints for a locked event.")

        if event and event.end_time and event.end_time < utc_now():
            raise BusinessLogicError("Cannot redeem hints after an event has ended.")

        hint = Hint.query.get(hint_id)
        if not hint:
            raise ValidationError(f"Hint {hint_id} not found.")

        if hint.challenge_id != challenge_id:
            raise BusinessLogicError("This hint does not belong to the specified challenge.")

        if cls.query.filter_by(team_id=team_id, hint_id=hint_id).first():
            raise BusinessLogicError("This hint has already been redeemed by your team.")

    @classmethod
    def create_redemption(
        cls,
        hint_id: int,
        user_id: int,
        team_id: int,
        challenge_id: int,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> HintRedemption:
        """Create a hint redemption and associated score event.

        Args:
            hint_id: ID of the hint being redeemed
            user_id: ID of the user redeeming
            team_id: ID of the team
            timestamp: When redeemed (defaults to now)
            commit: Whether to commit immediately

        Returns:
            HintRedemption: The created redemption
        """
        # LAZY-IMPORT
        from ...team.models.Team import Team

        team = db.session.get(Team, team_id)
        if not team:
            raise ValidationError(f"Team with ID {team_id} not found")

        cls.validate_redemption_allowed(user_id, team_id, hint_id, team.event_id, challenge_id)

        if timestamp is None:
            timestamp = utc_now()

        validated_data = cls.validate(
            {
                "hint_id": hint_id,
                "user_id": user_id,
                "team_id": team_id,
                "timestamp": timestamp.isoformat(),
            }
        )

        # LAZY-IMPORT
        from ...challenge.models.Hint import Hint

        hint = Hint.find_by_id(validated_data["hint_id"])
        points = -abs(hint.deduction) if hint.deduction > 0 else 0

        redemption = cls(
            hint_id=validated_data["hint_id"],
            user_id=validated_data["user_id"],
            team_id=validated_data["team_id"],
            timestamp=timestamp,
            points=points,
        )

        db.session.add(redemption)
        db.session.flush()

        if points != 0:
            # LAZY-IMPORT
            from .Score import Score
            from .ScoreEvent import ScoreEvent

            score = Score.find_by_team(team_id)
            score_event = ScoreEvent.create_score_event(
                score_id=score.id, team_id=team_id, points=points, timestamp=timestamp, commit=False
            )
            redemption.score_event = score_event

        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return redemption

    @classmethod
    def find_by_team_and_hint(cls, team_id: int, hint_id: int) -> HintRedemption | None:
        """
        Find redemption for a specific team and hint
        """
        return cls.query.filter_by(team_id=team_id, hint_id=hint_id).first()  # type: ignore[no-any-return]

    @classmethod
    def find_filtered_redemptions(
        cls,
        team_id: int | None = None,
        hint_id: int | None = None,
        challenge_id: int | None = None,
        user_id: int | None = None,
    ) -> list[HintRedemption]:
        """
        Find hint redemptions based on filters
        """
        # LAZY-IMPORT
        from ...challenge.models.Hint import Hint

        query = cls.query

        if team_id is not None:
            query = query.filter_by(team_id=team_id)
        if hint_id is not None:
            query = query.filter_by(hint_id=hint_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if challenge_id is not None:
            query = query.join(Hint).filter(Hint.challenge_id == challenge_id)

        return query.order_by(cls.timestamp.desc()).all()  # type: ignore[no-any-return]

    def delete_redemption(self, commit: bool = True) -> None:
        """
        Delete this redemption and its associated score event
        """
        if self.score_event:
            self.score_event.delete_event(commit=False)

        db.session.delete(self)
        if commit:
            db.session.commit()
