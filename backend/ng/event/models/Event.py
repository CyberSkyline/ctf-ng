"""
Defines the Event database model.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from CTFd.models import db
from sqlalchemy import CheckConstraint, func

from ... import config
from ...core.utils.validator import BaseValidator
from ...event.models.Demographic import Demographic
from ...core import BusinessLogicError


class Event(db.Model):
    __tablename__ = "ng_events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.EVENT_NAME_MAX_LENGTH), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    max_team_size = db.Column(db.Integer, default=config.MAX_TEAM_SIZE, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    locked = db.Column(db.Boolean, default=False, nullable=False)
    public = db.Column(db.Boolean, nullable=False, default=False)
    registration_open = db.Column(db.Boolean, nullable=False, default=False)
    registration_start_date = db.Column(db.DateTime, nullable=True)
    registration_end_date = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(start_time IS NULL AND end_time IS NULL) OR (start_time IS NOT NULL AND end_time IS NOT NULL)",
            name="ck_event_times_together",
        ),
        CheckConstraint(
            "start_time IS NULL OR end_time IS NULL OR start_time < end_time",
            name="ck_event_times_order",
        ),
        CheckConstraint(
            "(registration_start_date IS NULL AND registration_end_date IS NULL) OR "
            "(registration_start_date IS NOT NULL AND registration_end_date IS NOT NULL)",
            name="ck_event_registration_dates_together",
        ),
        CheckConstraint(
            "registration_start_date IS NULL OR registration_end_date IS NULL OR registration_start_date < registration_end_date",
            name="ck_event_registration_dates_order",
        ),
        {"extend_existing": True},
    )

    teams = db.relationship("Team", backref="event", cascade="all, delete-orphan")
    challenges = db.relationship("Challenge", back_populates="event", cascade="all, delete-orphan")

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
            "start_time": self.start_time.isoformat() + "Z" if self.start_time else None,
            "end_time": self.end_time.isoformat() + "Z" if self.end_time else None,
            "locked": self.locked,
            "public": self.public,
            "registration_open": self.registration_open,
            "registration_start_date": self.registration_start_date.isoformat() + "Z" if self.registration_start_date else None,
            "registration_end_date": self.registration_end_date.isoformat() + "Z" if self.registration_end_date else None,
        }

        return data

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
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
        validator.validate_boolean(
            data,
            "public",
            required=False,
            friendly_name="Public event",
        )
        validator.validate_boolean(
            data,
            "registration_open",
            required=False,
            friendly_name="Registration open status",
        )
        validator.validate_time_window(
            data,
            start_field="registration_start_date",
            end_field="registration_end_date",
        )

        return validator.validate()

    @classmethod
    def create_event(
        cls,
        name: str,
        description: str = "",
        max_team_size: int | None = config.MAX_TEAM_SIZE,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        locked: bool = False,
        public: bool = True,
        registration_open: bool = True,
        registration_start_date: datetime | None = None,
        registration_end_date: datetime | None = None,
        commit: bool = True,
    ):
        """Create and persist a new event to the database.

        Args:
            name (str): Event name
            description (str, optional): Event description
            max_team_size (int, optional): Maximum team size
            start_time (datetime, optional): Event start time
            end_time (datetime, optional): Event end time
            locked (bool, optional): Whether event is locked
            public (bool, optional): Whether event is public
            registration_open (bool, optional): Whether registration is open
            registration_start_date (datetime, optional): Registration start date
            registration_end_date (datetime, optional): Registration end date

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
            public=public,
            registration_open=registration_open,
            registration_start_date=registration_start_date,
            registration_end_date=registration_end_date,
        )

        db.session.add(event)
        if commit:
            db.session.commit()
        return event

    def update_event(self, commit=True, **kwargs) -> Event:
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
        return self

    def get_all_teams(self):
        from ...team.models.Team import Team

        return Team.query.filter_by(event_id=self.id).all()

    def get_all_challenges(self):
        from ...challenge.models.Challenge import Challenge

        return Challenge.query.filter_by(event_id=self.id).all()

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
    def get_all_events(cls, public_only=True) -> list[Event]:
        """Gets all events

        Returns:
            list: List of all <Event> objects in the database.
        """

        if public_only:
            return cls.query.filter_by(public=True).all()
        return cls.query.all()

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

    def check_eligibility(self, user):
        """Check if a user is eligible to register for an event.

        Args:
            user (User): The user object

        Returns:
            bool: True if eligible, False otherwise
        """
        if self.registration_open is False:
            raise BusinessLogicError("Event registration is closed.")

        if self.registration_end_date and datetime.utcnow() > self.registration_end_date:
            raise BusinessLogicError("Event registration has ended.")

        if self.registration_start_date and datetime.utcnow() < self.registration_start_date:
            raise BusinessLogicError("Event registration has not started yet.")

        if Demographic.find_by_user_and_event(user.id, self.id):
            raise BusinessLogicError("User is already registered for this event.")

        return True