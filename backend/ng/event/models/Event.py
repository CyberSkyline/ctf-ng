"""
/backend/ng/event/models/Event.py
Defines the Event database model, its columns, and relationships to other models.
"""

from CTFd.models import db
from sqlalchemy import CheckConstraint, func
from sqlalchemy.exc import IntegrityError
from typing import Any
from ... import config


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
    )

    teams = db.relationship("Team", backref="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.name}>"

    @classmethod
    def create_event(
        cls,
        name,
        description=None,
        max_team_size=None,
        start_time=None,
        end_time=None,
        locked=False,
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
        if max_team_size is None:
            max_team_size = config.MAX_TEAM_SIZE

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

    def update_event(self, **kwargs):
        """Update event properties and persist to database.

        Args:
            **kwargs: Event properties to update

        Returns:
            bool: True if successful

        Raises:
            IntegrityError: If database constraints are violated
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise

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
    def get_events_with_stats(cls) -> list[dict[str, Any]]:
        """Gets all events with their team and member stats.

        Returns:
            list[dict]: List of events with stats data.
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

        return [
            {
                "id": event_id,
                "name": name,
                "description": description,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "locked": locked,
                "team_count": team_count,
                "total_members": total_members,
            }
            for (
                event_id,
                name,
                description,
                start_time,
                end_time,
                locked,
                team_count,
                total_members,
            ) in event_stats
        ]

    def get_event_details_with_teams(self) -> dict[str, Any]:
        """Gets detailed info about this event including all its teams.

        Returns:
            dict: Event details and teams data.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        # Single join query to get teams with member counts, avoids N+1 queries
        teams_with_counts = (
            db.session.query(
                Team.id,
                Team.name,
                Team.ranked,
                func.count(TeamMember.id).label("member_count"),
            )
            .outerjoin(TeamMember, Team.id == TeamMember.team_id)
            .filter(Team.event_id == self.id)
            .group_by(Team.id, Team.name, Team.ranked)
            .all()
        )

        total_members = TeamMember.query.filter_by(event_id=self.id).count()

        teams_data = [
            {
                "id": team_id,
                "name": name,
                "member_count": member_count,
                "max_team_size": self.max_team_size,
                "is_full": member_count >= self.max_team_size,
                "ranked": ranked,
            }
            for team_id, name, ranked, member_count in teams_with_counts
        ]

        event_data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "max_team_size": self.max_team_size,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "locked": self.locked,
            "team_count": len(teams_data),
            "total_members": total_members,
        }

        return {"event": event_data, "teams": teams_data}

    def serialize(self):
        """Returns a dictionary representation of the Event model."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "max_team_size": self.max_team_size,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "locked": self.locked,
        }

    def get_largest_team_size(self) -> int:
        """Get the size of the largest team in this event.

        Returns:
            int: Size of the largest team, or 0 if no teams exist.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.Team import Team

        return db.session.query(func.max(Team.member_count)).filter(Team.event_id == self.id).scalar() or 0

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
