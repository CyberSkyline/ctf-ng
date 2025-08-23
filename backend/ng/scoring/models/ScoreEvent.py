"""
Defines the ScoreEvent model for tracking all scoring changes.
"""

from __future__ import annotations
from typing import (
    Any,
    TypedDict,
    NotRequired,
)

from datetime import datetime
from sqlalchemy.orm import selectinload

from CTFd.models import db

from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator


class SerializedScoreEvent(TypedDict):
    id: int
    score_id: int
    team_id: int
    points: int
    timestamp: str
    # Name enrichment fields
    team_name: NotRequired[str]
    source_type: NotRequired[str]
    source: NotRequired[dict[str, Any]]


class ScoreEvent(db.Model):
    __tablename__ = "ng_score_events"

    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey("ng_scores.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)

    score = db.relationship("Score", back_populates="events")
    team = db.relationship("Team", backref="score_events")

    attempts = db.relationship("Attempt", back_populates="score_event")
    hint_redemptions = db.relationship("HintRedemption", back_populates="score_event")
    manual_awards = db.relationship("ManualPointAward", back_populates="score_event")

    def __repr__(self):
        return f"<ScoreEvent {self.id}: team={self.team_id} points={self.points}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedScoreEvent:
        """
        Serialize score event for API response with embedded source data
        """
        data = {
            "id": self.id,
            "score_id": self.score_id,
            "team_id": self.team_id,
            "points": self.points,
            "timestamp": self.timestamp.isoformat() + "Z",
        }

        if self.team:
            data["team_name"] = self.team.name

        if include_admin_fields:
            if self.attempts and len(self.attempts) > 0:
                data["source_type"] = "attempt"
                data["source"] = self.attempts[0].serialize(include_admin_fields=include_admin_fields)
            elif self.hint_redemptions and len(self.hint_redemptions) > 0:
                data["source_type"] = "hint_redemption"
                data["source"] = self.hint_redemptions[0].serialize(include_admin_fields=include_admin_fields)
            elif self.manual_awards and len(self.manual_awards) > 0:
                data["source_type"] = "manual_award"
                data["source"] = self.manual_awards[0].serialize(include_admin_fields=include_admin_fields)

        return SerializedScoreEvent(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate score event data
        """
        validator = BaseValidator()

        validator.validate_model_id(data, "score_id", "Score", required=True)
        validator.validate_model_id(data, "team_id", "Team", required=True)

        validator.validate_integer(data, "points", required=True, allow_zero=False)

        validator.validate_datetime(data, "timestamp", required=False)

        return validator.validate()  # type: ignore[no-any-return]

    @classmethod
    def create_score_event(
        cls,
        score_id: int,
        team_id: int,
        points: int,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> ScoreEvent:
        """Create a score event and update the associated score.

        Args:
            score_id: ID of the associated Score
            team_id: ID of the team
            points: Points to add/subtract (can be negative)
            timestamp: When the event occurred (defaults to now)
            commit: Whether to commit immediately

        Returns:
            ScoreEvent: The created score event
        """
        if timestamp is None:
            timestamp = utc_now()

        validated_data = cls.validate(
            {
                "score_id": score_id,
                "team_id": team_id,
                "points": points,
                "timestamp": timestamp.isoformat(),
            }
        )

        event = cls(
            score_id=validated_data["score_id"],
            team_id=validated_data["team_id"],
            points=validated_data["points"],
            timestamp=timestamp,
        )

        db.session.add(event)
        db.session.flush()

        # LAZY-IMPORT
        from .Score import Score

        score = Score.query.get(validated_data["score_id"])
        score.adjust(validated_data["points"], commit=False)

        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return event

    @classmethod
    def find_filtered_events(
        cls,
        score_id: int | None = None,
        team_id: int | None = None,
        event_id: int | None = None,
        eager_load_source: bool = False,
    ) -> list[ScoreEvent]:
        """
        Finds a list of score events based on filters.

        Args:
            score_id: Filter by score ID
            team_id: Filter by team ID
            event_id: Filter by event ID
            eager_load_source: If True, eagerly loads the source relationships
                              (attempts, hint_redemptions, manual_awards)
        """
        # LAZY-IMPORT
        from .Score import Score

        query = cls.query

        if score_id is not None:
            query = query.filter_by(score_id=score_id)
        if team_id is not None:
            query = query.filter_by(team_id=team_id)
        if event_id is not None:
            query = query.join(Score).filter(Score.event_id == event_id)

        # Eager load source relationships if requested
        if eager_load_source:
            query = query.options(
                selectinload(cls.attempts), selectinload(cls.hint_redemptions), selectinload(cls.manual_awards)
            )

        query = query.order_by(cls.timestamp.desc())
        return query.all()  # type: ignore[no-any-return]

    def delete_event(self, commit: bool = True) -> None:
        """
        Delete this score event and adjust the associated score
        """
        self.score.adjust(-self.points, commit=commit)

        db.session.delete(self)
        if commit:
            db.session.commit()
