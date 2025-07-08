"""
Defines the Event database model.
"""

from __future__ import annotations
from typing import Any

from sqlalchemy import CheckConstraint, func
from CTFd.models import db

from ... import config
from ...core.utils.validator import BaseValidator
from ...core.exceptions import ValidationError


class Event(db.Model):
    __tablename__ = "ng_events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.EVENT_NAME_MAX_LENGTH), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    max_team_size = db.Column(db.Integer, default=config.MAX_TEAM_SIZE, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    locked = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(start_time IS NULL AND end_time IS NULL) OR (start_time IS NOT NULL AND end_time IS NOT NULL)",
            name="ck_event_times_together",
        ),
        CheckConstraint(
            "start_time IS NULL OR end_time IS NULL OR start_time < end_time",
            name="ck_event_times_order",
        ),
        {"extend_existing": True},
    )

    teams = db.relationship("Team", backref="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.name}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize event for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized event data
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "max_team_size": self.max_team_size,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "locked": self.locked,
        }

        return data

    @classmethod
    def validate(
        cls,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            config.EVENT_NAME_MAX_LENGTH,
            required=True,
            friendly_name="Event name",
        )
        validator.validate_string(
            data,
            "description",
            config.EVENT_DESCRIPTION_MAX_LENGTH,
            required=False,
            friendly_name="Event description",
        )
        validator.validate_integer_range(
            data,
            "max_team_size",
            1,
            config.MAX_TEAM_SIZE,
            required=True,
            friendly_name="Max team size",
        )
        validator.validate_boolean(
            data,
            "locked",
            required=False,
            friendly_name="Locked status",
        )
        validator.validate_time_window(
            data,
            start_field="start_time",
            end_field="end_time",
        )

        is_valid, errors, parsed_data = validator.is_valid()
        if not is_valid:
            raise ValidationError("Event data is invalid.", errors=errors)
        return parsed_data

    @classmethod
    def create_event(
        cls,
        name: str,
        description: str = "",
        max_team_size: int = config.MAX_TEAM_SIZE,
        start_time=None,
        end_time=None,
        locked: bool = False,
    ):
        """Create and persist a new event to the database.

        Args:
            name (str): Event name
            description (str, optional): Event description
            max_team_size (int, optional): Maximum team size
            start_time (datetime, optional): Event start time
            end_time (datetime, optional): Event end time
            locked (bool, optional): Whether event is locked

        Returns:
            Event: The created event instance
        """

        event = cls(
            name=name,
            description=description,
            max_team_size=max_team_size,
            start_time=start_time,
            end_time=end_time,
            locked=locked,
        )

        db.session.add(event)
        db.session.commit()
        return event

    def update_event(self, commit=True, **kwargs):
        """Update event properties and persist to database.

        Args:
            commit: Whether to commit changes immediately
            **kwargs: Event properties to update

        Returns:
            bool: True if successful
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        Event.validate(self.serialize())

        if commit:
            db.session.commit()

        return True

    def get_all_teams(self):
        from ...team.models.Team import Team

        return Team.query.filter_by(event_id=self.id).all()

    @classmethod
    def find_by_id(cls, event_id: int):
        """Find an event by ID.

        Args:
            event_id (int): The event ID to find

        Returns:
            Event or None: The event instance if found, None otherwise
        """
        return cls.query.get(event_id)

    @classmethod
    def find_by_name(cls, name: str):
        """Find an event by name.

        Args:
            name (str): The event name to find

        Returns:
            Event or None: The event instance if found, None otherwise
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_events_with_stats(cls):
        """Gets all events with their team and member stats.

        Returns:
            list: Raw query results (Row objects) with event stats
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        event_stats = (
            db.session.query(
                cls.id,
                cls.name,
                cls.description,
                cls.start_time,
                cls.end_time,
                cls.locked,
                func.count(Team.id.distinct()).label("team_count"),
                func.count(TeamMember.id).label("total_members"),
            )
            .outerjoin(Team, cls.id == Team.event_id)
            .outerjoin(TeamMember, cls.id == TeamMember.event_id)
            .group_by(
                cls.id,
                cls.name,
                cls.description,
                cls.start_time,
                cls.end_time,
                cls.locked,
            )
            .all()
        )

        return event_stats

    def get_event_details_with_teams(self) -> dict[str, Any]:
        """
        Gets detailed info about this event, including all its associated teams.

        Returns:
            A dictionary containing the raw <Event> object (self) and a raw
            list of <Team> objects associated with it.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        teams_in_event = Team.query.filter_by(event_id=self.id).all()

        self.team_count = len(teams_in_event)
        self.total_members = TeamMember.query.filter_by(event_id=self.id).count()

        return {"event": self, "teams": teams_in_event}

    def get_team_count(self) -> int:
        """Get the number of teams in this event.

        Returns:
            int: Number of teams in this event.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team

        return Team.query.filter_by(event_id=self.id).count()

    @classmethod
    def get_total_count(cls) -> int:
        """Get the total count of all events.

        Returns:
            int: Total number of events
        """
        return cls.query.count()

    @classmethod
    def get_events_with_detailed_stats(cls):
        """Gets all events with their detailed team and member stats.

        Returns:
            list: Raw query results with event statistics
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        event_stats_query = (
            db.session.query(
                cls.id,
                cls.name,
                cls.start_time,
                cls.end_time,
                func.count(Team.id.distinct()).label("teams"),
                func.count(TeamMember.id).label("total_members"),
            )
            .outerjoin(Team, cls.id == Team.event_id)
            .outerjoin(TeamMember, cls.id == TeamMember.event_id)
            .group_by(cls.id, cls.name, cls.start_time, cls.end_time)
            .all()
        )

        return event_stats_query

    @classmethod
    def delete_all(cls) -> None:
        """Delete all events from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
