"""
Defines the Demographic model for tracking user event registrations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from CTFd.models import db

from ...core.utils import utc_now


class Demographic(db.Model):
    __tablename__ = "ng_demographics"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    reg_timestamp = db.Column(db.DateTime, default=utc_now, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="uq_demographic_user_event"),)

    def __repr__(self):
        return f"<Demographic user_id={self.user_id} event_id={self.event_id}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize demographic for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized demographic data
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "reg_timestamp": self.reg_timestamp,
        }

        return data

    @classmethod
    def create_demographic(
        cls,
        user_id: int,
        event_id: int,
        reg_timestamp: datetime | None = None,
        commit: bool = True,
    ) -> Demographic:
        """Create and persist a new demographic entry.

        Args:
            user_id: User ID
            event_id: Event ID
            reg_timestamp: Registration timestamp (defaults to now)
            commit: Whether to commit immediately

        Returns:
            Demographic: The created instance
        """
        if reg_timestamp is None:
            reg_timestamp = utc_now()

        demographic = cls(
            user_id=user_id,
            event_id=event_id,
            reg_timestamp=reg_timestamp,
        )

        db.session.add(demographic)
        if commit:
            db.session.commit()
        return demographic

    @classmethod
    def find_by_user_and_event(cls, user_id: int, event_id: int) -> Demographic | None:
        """Find demographic entry for a user in an event.

        Args:
            user_id: User ID
            event_id: Event ID

        Returns:
            Demographic or None: The demographic if found
        """
        return cls.query.filter_by(user_id=user_id, event_id=event_id).first()

    def delete(self, commit: bool = True) -> None:
        """Delete this demographic entry.

        Args:
            commit: Whether to commit immediately
        """
        db.session.delete(self)
        if commit:
            db.session.commit()
