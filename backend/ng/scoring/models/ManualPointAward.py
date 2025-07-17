"""
Defines the ManualPointAward model for admin point adjustments.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from CTFd.models import db, Users

from ...core.utils import utc_now
from ...core.validation import BaseValidator


class SerializedManualPointAward(TypedDict):
    id: int
    admin_id: int
    team_id: int
    score_event_id: int
    timestamp: str
    points: int
    reason: str


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
            "timestamp": self.timestamp.isoformat() + "Z" if self.timestamp else None,
            "points": self.points,
            "reason": self.reason,
        }

        if include_admin_fields and self.admin:
            data["admin_name"] = self.admin.name

        return SerializedManualPointAward(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate manual point award data
        """
        validator = BaseValidator()
        
        if "admin_id" not in data:
            validator.errors["admin_id"] = "Admin ID is required"
        else:
            admin = Users.query.get(data["admin_id"])
            if not admin:
                validator.errors["admin_id"] = f"Admin with ID {data['admin_id']} not found"
            elif admin.type != "admin":
                validator.errors["admin_id"] = "User must be an admin to award points"
            else:
                validator._add_parsed_data("admin_id", data["admin_id"])
        
        validator.validate_model_id(data, "team_id", "Team", required=True)
        
        if "points" not in data:
            validator.errors["points"] = "Points value is required"
        else:
            try:
                points = int(data["points"])
                if points == 0:
                    validator.errors["points"] = "Points cannot be zero"
                else:
                    validator._add_parsed_data("points", points)
            except (ValueError, TypeError):
                validator.errors["points"] = "Points must be a valid integer"
        

        validator.validate_string(
            data,
            "reason",
            max_length=config.MANUAL_AWARD_REASON_MAX_LENGTH,
            required=True,
            friendly_name="Reason"
        )
        
        validator.validate_optional_timestamp(data)
        
        return validator.validate()

    @classmethod
    def validate_api_award(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate manual point award from API (partial data)
        """
        validator = BaseValidator()
        
        if "points" not in data:
            validator.errors["points"] = "Points value is required"

        elif not isinstance(data["points"], int) or data["points"] == 0:
            validator.errors["points"] = "Points must be a non-zero integer"
        else:
            validator._add_parsed_data("points", data["points"])
        
        validator.validate_string(
            data,
            "reason",
            config.MANUAL_AWARD_REASON_MAX_LENGTH,
            required=True,
            friendly_name="Reason"
        )        
        return validator.validate()


    @classmethod
    def create_award(
        cls,
        admin_id: int,
        team_id: int,
        points: int,
        reason: str,
        event_id: int,
        timestamp: datetime | None = None,
        commit: bool = True,
    ) -> ManualPointAward:
        """Create a manual point award and associated score event.
        
        Args:
            admin_id: ID of the admin awarding points
            team_id: ID of the team receiving points
            points: Points to add/subtract (can be negative)
            reason: Explanation for the award
            event_id: ID of the event (for finding the score)
            timestamp: When awarded (defaults to now)
            commit: Whether to commit immediately
            
        Returns:
            ManualPointAward: The created award
        """
        if timestamp is None:
            timestamp = utc_now()
            
        validated_data = cls.validate({
            "admin_id": admin_id,
            "team_id": team_id,
            "points": points,
            "reason": reason,
            "timestamp": timestamp,
        })
        
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from .Score import Score
        from .ScoreEvent import ScoreEvent
        
        score = Score.find_by_team_and_event(validated_data["team_id"], event_id)
        if not score:
            raise ValidationError(f"Team {validated_data['team_id']} has no score in event {event_id}")
        
        score_event = ScoreEvent.create_score_event(
            score_id=score.id,
            team_id=validated_data["team_id"],
            points=validated_data["points"],
            timestamp=validated_data.get("timestamp", timestamp),
            commit=False
        )
        
        award = cls(
            admin_id=validated_data["admin_id"],
            team_id=validated_data["team_id"],
            score_event_id=score_event.id,
            timestamp=validated_data.get("timestamp", timestamp),
            points=validated_data["points"],
            reason=validated_data["reason"],
        )
        
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
        return query.all()

    def delete_award(self, commit: bool = True) -> None:
        """
        Delete this award and its associated score event
        """
        if self.score_event:
            self.score_event.delete_event(commit=False)
            
        db.session.delete(self)
        if commit:
            db.session.commit()


