"""
Defines the ManualPointAward model for admin point adjustments.
"""

from __future__ import annotations
from typing import Any, TypedDict, NotRequired

from datetime import datetime

from CTFd.models import db

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator


class SerializedManualPointAward(TypedDict):
    id: int
    admin_id: int
    team_id: int
    score_event_id: int
    timestamp: str
    points: int
    reason: str
    admin_name: NotRequired[str]
    team_name: NotRequired[str]


class ManualPointAward(db.Model):
    __tablename__ = "ng_manual_point_awards"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    score_event_id = db.Column(db.Integer, db.ForeignKey("ng_score_events.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(config.MANUAL_AWARD_REASON_MAX_LENGTH), nullable=False)

    admin = db.relationship("Users", backref="manual_point_awards")
    team = db.relationship("Team", backref="manual_point_awards")
    score_event = db.relationship("ScoreEvent", back_populates="manual_awards", uselist=False)

    def __repr__(self):
        return f"<ManualPointAward {self.id}: team={self.team_id} points={self.points}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedManualPointAward:
        """
        Serialize manual point award for API response
        """
        data = {
            "id": self.id,
            "admin_id": self.admin_id,
            "team_id": self.team_id,
            "score_event_id": self.score_event_id,
            "timestamp": self.timestamp.isoformat() + "Z",
            "points": self.points,
            "reason": self.reason,
        }

        if self.admin:
            data["admin_name"] = self.admin.name
        if self.team:
            data["team_name"] = self.team.name

        return SerializedManualPointAward(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate manual point award data
        """
        validator = BaseValidator()

        validator.validate_admin_id(data, "admin_id", required=True)

        validator.validate_model_id(data, "team_id", "Team", required=True)

        validator.validate_integer(data, "points", allow_zero=False, required=True, friendly_name="Points")

        validator.validate_string(
            data, "reason", max_length=config.MANUAL_AWARD_REASON_MAX_LENGTH, required=True, friendly_name="Reason"
        )

        validator.validate_datetime(data, "timestamp", required=False)

        return validator.validate()  # type: ignore[no-any-return]

    @classmethod
    def create_award(
        cls,
        admin_id: int,
        team_id: int,
        points: int,
        reason: str,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> ManualPointAward:
        """Create a manual point award and associated score event.

        Args:
            admin_id: ID of the admin awarding points
            team_id: ID of the team receiving points
            points: Points to add/subtract (can be negative)
            reason: Explanation for the award
            timestamp: When awarded (defaults to now)
            commit: Whether to commit immediately

        Returns:
            ManualPointAward: The created award
        """
        if timestamp is None:
            timestamp = utc_now()

        validated_data = cls.validate(
            {
                "admin_id": admin_id,
                "team_id": team_id,
                "points": points,
                "reason": reason,
            }
        )

        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from .Score import Score
        from .ScoreEvent import ScoreEvent

        score = Score.find_by_team(validated_data["team_id"])

        score_event = ScoreEvent.create_score_event(
            score_id=score.id,
            team_id=validated_data["team_id"],
            points=validated_data["points"],
            timestamp=timestamp,
            commit=False,
        )

        award = cls(
            admin_id=validated_data["admin_id"],
            team_id=validated_data["team_id"],
            timestamp=timestamp,
            points=validated_data["points"],
            reason=validated_data["reason"],
        )

        award.score_event = score_event

        db.session.add(award)

        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return award

    @classmethod
    def find_filtered_awards(
        cls,
        team_id: int | None = None,
        admin_id: int | None = None,
        event_id: int | None = None,
        limit: int | None = None,
    ) -> list[ManualPointAward]:
        """
        Find manual point awards based on filters
        """
        # LAZY-IMPORT
        from .Score import Score
        from .ScoreEvent import ScoreEvent

        query = cls.query

        if team_id is not None:
            query = query.filter(cls.team_id == team_id)
        if admin_id is not None:
            query = query.filter(cls.admin_id == admin_id)
        if event_id is not None:
            query = query.join(ScoreEvent).join(Score).filter(Score.event_id == event_id)

        query = query.order_by(cls.timestamp.desc())

        if limit is not None:
            query = query.limit(limit)
        return query.all()  # type: ignore[no-any-return]

    def delete_award(self, commit: bool = True) -> None:
        """
        Delete this award and its associated score event
        """
        if self.score_event:
            self.score_event.delete_event(commit=False)

        db.session.delete(self)
        if commit:
            db.session.commit()
