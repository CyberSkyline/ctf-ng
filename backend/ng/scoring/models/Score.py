"""
Defines the Score model for tracking team scores per event.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, NotRequired, TypedDict

from CTFd.models import db
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ... import config
from ...core.exceptions import NotFoundError
from ...core.utils import utc_now
from ...core.utils.cache import (
    clear_cache_for_function,
    clear_cache_for_function_with_prefix,
    memoize,
)
from ...core.utils.validator import BaseValidator
from ...team.models.TeamMember import TeamMember


class SerializedScore(TypedDict):
    id: int
    team_id: int
    event_id: int
    event_name: NotRequired[str]
    points: int
    last_correct_offset: int
    last_update: str
    team_name: str | None


class Score(db.Model):
    __tablename__ = "ng_scores"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    points = db.Column(db.Integer, default=0, nullable=False)
    last_correct_offset = db.Column(db.BigInteger, default=0, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    team_name = db.Column(db.String(config.TEAM_NAME_MAX_LENGTH), nullable=False)  # Cached for leaderboard performance

    __table_args__ = (
        db.UniqueConstraint("team_id", "event_id", name="uq_score_team_event"),
        db.Index("ix_ng_scores_event_points", "event_id", "points"),
    )

    team = db.relationship("Team", backref="scores")
    event = db.relationship("Event", backref="scores")
    events = db.relationship("ScoreEvent", back_populates="score", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Score {self.id}: team={self.team_id} event={self.event_id} points={self.points}>"

    def serialize(self, include_admin_fields: bool = False) -> SerializedScore:
        """
        Serialize score for API response
        """
        data = {
            "id": self.id,
            "team_id": self.team_id,
            "event_id": self.event_id,
            "points": self.points,
            "last_correct_offset": self.last_correct_offset,
            "last_update": self.last_update.isoformat() + "Z",
            "team_name": self.team_name,
        }

        if self.event:
            data["event_name"] = self.event.name

        return SerializedScore(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate score data.
        """
        validator = BaseValidator()

        validator.validate_model_id(data, "team_id", "Team", required=True)
        validator.validate_model_id(data, "event_id", "Event", required=True)
        validator.validate_integer(data, "points", required=False)
        validator.validate_integer(data, "last_correct_offset", required=False)

        validator.validate_string(
            data, "team_name", config.TEAM_NAME_MAX_LENGTH, required=True, friendly_name="Team name"
        )

        validator.validate_datetime(data, "last_update", required=False)

        return validator.validate()  # type: ignore[no-any-return]

    @classmethod
    def create_score(
        cls,
        team_id: int,
        points: int = 0,
        last_correct_offset: int = 0,
        last_update: datetime | None = None,
        commit: bool = True,
        team=None,
    ) -> Score:
        """Create a new score record for a team.

        Args:
            team_id: ID of the team
            points: Initial points (defaults to 0)
            last_update: Timestamp (defaults to now)
            commit: Whether to commit immediately

        Returns:
            Score: The created score instance
        """
        if last_update is None:
            last_update = utc_now()

        if team is None:
            # LAZY-IMPORT
            from ...team.models.Team import Team

            team = Team.find_by_id(team_id)

        validated_data = cls.validate(
            {
                "team_id": team_id,
                "event_id": team.event_id,
                "team_name": team.name,
                "points": points,
                "last_correct_offset": last_correct_offset,
                "last_update": last_update.isoformat(),
            }
        )

        score = cls(
            team_id=validated_data["team_id"],
            event_id=validated_data["event_id"],
            team_name=validated_data["team_name"],
            points=validated_data.get("points", 0),
            last_correct_offset=validated_data.get("last_correct_offset", 0),
            last_update=last_update,
        )

        db.session.add(score)
        if commit:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return score

    def adjust(self, delta: int, commit: bool = True) -> None:
        """Adjust the score by a delta value.

        Args:
            delta: Points to add (can be negative)
            commit: Whether to commit immediately
        """
        self.points += delta
        self.last_update = utc_now()

        if commit:
            db.session.commit()

        Score.clear_leaderboard_cache(event_id=self.event_id)

    def mark_correct_submission(self, timestamp : datetime | None = None, commit : bool = True) -> None:
        """
        Adjust the offset for the last correct submission
        """
        if not timestamp:
            timestamp = utc_now()

        delta = timestamp.replace(tzinfo=None) - self.team.start_timestamp.replace(tzinfo=None)
        self.last_correct_offset = delta / timedelta(milliseconds=1)

        if commit:
            db.session.commit()

    def recalculate(self, commit: bool = True) -> None:
        """
        Recalculate score by summing all ScoreEvents.
        """
        # LAZY-IMPORT
        from .Attempt import Attempt
        from .ScoreEvent import ScoreEvent

        total = db.session.query(func.sum(ScoreEvent.points)).filter_by(score_id=self.id).scalar() or 0
        most_recent_correct_attempt = (
            db.session.query(Attempt)
            .filter_by(team_id=self.team_id, is_correct=True)
            .order_by(Attempt.timestamp.desc())
            .first()
        )

        self.points = total
        self.last_update = utc_now()

        if most_recent_correct_attempt:
            delta = most_recent_correct_attempt.timestamp.replace(tzinfo=None) - self.team.start_timestamp.replace(tzinfo=None)
            self.last_correct_offset = delta / timedelta(milliseconds=1)
        else:
            self.last_correct_offset = 0

        if commit:
            db.session.commit()

        Score.clear_leaderboard_cache(event_id=self.event_id)

    @classmethod
    @memoize(timeout=config.LEADERBOARD_CACHE_TIMEOUT if hasattr(config, "LEADERBOARD_CACHE_TIMEOUT") else 60)
    def get_leaderboard(cls, event_id: int, limit: int | None = None) -> list[SerializedScore]:
        """Get the leaderboard for an event, sorted by points descending

        Args:
            event_id: The event to get leaderboard for
            limit: Optional limit on number of results

        Returns:
            List of serialized scores ordered by points
        """
        # LAZY-IMPORT
        from ...team.models.Team import Team
        query = (
            cls.query
            .join(cls.team)
            .filter(cls.event_id == event_id)
            .filter(
                Team.ranked.is_(True),
                Team.start_timestamp.isnot(None),
            )
            .options(
                joinedload(Score.team)
                .joinedload(Team.members)
                .joinedload(TeamMember.sponsor)
            )
            .order_by(cls.points.desc(), cls.last_correct_offset.asc())
        )
        if limit:
            query = query.limit(limit)

        scores = query.all()
        leaderboard_data = []
        for score in scores:
            # Deduplicate sponsors
            sponsors_by_id = {
                member.sponsor.id: member.sponsor.serialize()
                for member in score.team.members
                if member.sponsor is not None
            }

            serialized_score = score.serialize()
            serialized_score["sponsors"] = list(sponsors_by_id.values())
            leaderboard_data.append(serialized_score)


        return leaderboard_data

    @classmethod
    def get_team_rank(cls, team_id: int) -> int | None:
        """Get the rank of a team in their event.

        Returns:
            Rank (1-indexed) or None if team not found
        """
        # LAZY-IMPORT
        from ...team.models.Team import Team

        team = Team.query.get(team_id)
        if not team:
            return None

        score = cls.find_by_team(team_id)
        if not score:
            return None

        higher_scores = cls.query.filter(cls.event_id == team.event_id, cls.points > score.points).count()

        return higher_scores + 1  # type: ignore[no-any-return]

    @classmethod
    def find_by_team(cls, team_id: int) -> Score:
        """
        Find score for a specific team. Creates one if it doesn't exist.
        """
        # LAZY-IMPORT
        from ...team.models.Team import Team

        team = Team.find_by_id(team_id)
        if not team:
            raise NotFoundError(f"Team with ID {team_id} not found")

        score = cls.query.filter_by(team_id=team_id, event_id=team.event_id).first()

        if score:
            return score  # type: ignore[no-any-return]

        score = cls.create_score(team_id=team_id, points=0, team=team)

        return score  # type: ignore[no-any-return]

    @classmethod
    def find_filtered_scores(
        cls,
        event_id: int | None = None,
        team_id: int | None = None,
        order_by_points: bool = False,
        limit: int | None = None,
    ) -> list[Score]:
        """
        Finds a list of scores based on filters
        """
        query = cls.query

        if event_id is not None:
            query = query.filter_by(event_id=event_id)
        if team_id is not None:
            query = query.filter_by(team_id=team_id)
        if order_by_points:
            query = query.order_by(cls.points.desc())
        else:
            query = query.order_by(cls.id.asc())

        if limit is not None:
            query = query.limit(limit)
        return query.all()  # type: ignore[no-any-return]

    @classmethod
    def clear_leaderboard_cache(cls, event_id: int | None = None) -> None:
        """
        Clear leaderboard cache for specific event or all events
        """
        if event_id is None:
            clear_cache_for_function("get_leaderboard")
        else:
            clear_cache_for_function_with_prefix("get_leaderboard", f"({event_id},")


    def delete(self, commit: bool = True) -> None:
        """Delete this score from the database."""
        db.session.delete(self)
        if commit:
            db.session.commit()
