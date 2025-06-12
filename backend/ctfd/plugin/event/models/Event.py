"""
/backend/ctfd/plugin/event/models/Event.py
Defines the Event database model, its columns, and relationships to other models.
"""

from CTFd.models import db
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import IntegrityError
from ... import config


class Event(db.Model):
    __tablename__ = "ng_events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.EVENT_NAME_MAX_LENGTH), nullable=False)
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

    teams = db.relationship("Team", backref="event", lazy=True)

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
