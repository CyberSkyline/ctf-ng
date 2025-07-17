"""
Defines the ScoreEvent model for tracking all scoring changes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from CTFd.models import db

from ...core.utils import utc_now
from ...core.validation import BaseValidator


class SerializedScoreEvent(TypedDict):
    id: int
    score_id: int
    team_id: int
    points: int
    timestamp: str


class ScoreEvent(db.Model):
    __tablename__ = "ng_score_events"

    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey("ng_scores.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)

    score = db.relationship("Score", back_populates="events")
    team = db.relationship("Team", backref="score_events")

    attempts = db.relationship("Attempt", back_populates="score_event", cascade="all, delete-orphan")
    hint_redemptions = db.relationship("HintRedemption", back_populates="score_event", cascade="all, delete-orphan")
    manual_awards = db.relationship("ManualPointAward", back_populates="score_event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScoreEvent {self.id}: team={self.team_id} points={self.points}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedScoreEvent:
        """
        Serialize score event for API response
        """
        data = {
            "id": self.id,
            "score_id": self.score_id,
            "team_id": self.team_id,
            "points": self.points,
            "timestamp": self.timestamp.isoformat() + "Z" if self.timestamp else None,
        }

        return SerializedScoreEvent(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate score event data
        """
        validator = BaseValidator()
        
        validator.validate_model_id(data, "score_id", "Score", required=True)
        validator.validate_model_id(data, "team_id", "Team", required=True)
        
        if "points" not in data:
            validator.errors["points"] = "Points value is required"
        elif not isinstance(data.get("points"), int):
            validator.errors["points"] = "Points must be an integer"
        elif data["points"] == 0:
            validator.errors["points"] = "Points cannot be zero"
        else:
            validator._add_parsed_data("points", data["points"])
        
        validator.validate_optional_timestamp(data)
        
        return validator.validate()

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
            
        validated_data = cls.validate({
            "score_id": score_id,
            "team_id": team_id,
            "points": points,
            "timestamp": timestamp,
        })
        
        event = cls(
            score_id=validated_data["score_id"],
            team_id=validated_data["team_id"],
            points=validated_data["points"],
            timestamp=validated_data.get("timestamp", timestamp),
        )
        
        db.session.add(event)
        db.session.flush()
        
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from .Score import Score

        score = Score.query.get(score_id)
        if score:
            score.adjust(points)
        
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
        limit: int | None = None,
    ) -> list[ScoreEvent]:
        """
        Finds a list of score events based on filters.
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
   
        query = query.order_by(cls.timestamp.desc())    
        if limit is not None:
            query = query.limit(limit)    
        return query.all()

    def delete_event(self, commit: bool = True) -> None:
        """
        Delete this score event and adjust the associated score
        """
        if self.score:
            self.score.adjust(-self.points)
            
        db.session.delete(self)
        if commit:
            db.session.commit()

