"""
Defines the EventRegistration model for event registration configuration.
"""

from __future__ import annotations
from typing import Any

from datetime import datetime
from sqlalchemy import CheckConstraint

from CTFd.models import db

from ...core.utils.validator import BaseValidator
from ...core.exceptions import ValidationError

class EventRegistration(db.Model):
    __tablename__ = "ng_event_registrations"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("ng_events.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    public = db.Column(db.Boolean, nullable=False, default=False)
    reg_open = db.Column(db.Boolean, nullable=False, default=False)
    reg_start_date = db.Column(db.DateTime, nullable=True)
    reg_end_date = db.Column(db.DateTime, nullable=True)

    event = db.relationship("Event", backref=db.backref("registration", uselist=False))

    __table_args__ = (
        CheckConstraint(
            "(reg_start_date IS NULL AND reg_end_date IS NULL) OR "
            "(reg_start_date IS NOT NULL AND reg_end_date IS NOT NULL)",
            name="ck_event_reg_dates_together",
        ),
        CheckConstraint(
            "reg_start_date IS NULL OR reg_end_date IS NULL OR reg_start_date < reg_end_date",
            name="ck_event_reg_dates_order",
        ),
    )

    def __repr__(self):
        return f"<EventRegistration event_id={self.event_id} reg_open={self.reg_open}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize event registration for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized event registration data
        """
        data = {
            "id": self.id,
            "event_id": self.event_id,
            "public": self.public,
            "reg_open": self.reg_open,
            "reg_start_date": self.reg_start_date,
            "reg_end_date": self.reg_end_date,
        }

        return data

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate event registration data.

        Args:
            data: Data to validate

        Returns:
            dict: Validated data

        Raises:
            ValidationError: If validation fails
        """
        validator = BaseValidator()

        validator.validate_positive_integer(data, "event_id", required=True)
        validator.validate_boolean(data, "reg_open", required=False)
        validator.validate_boolean(data, "public", required=False)

        validator.validate_time_window(
            data,
            start_field="reg_start_date",
            end_field="reg_end_date",
        )

        is_valid, errors, parsed_data = validator.is_valid()
        if not is_valid:
            raise ValidationError("Event registration data is invalid.", errors=errors)

        return parsed_data

    @classmethod
    def find_by_event_id(cls, event_id: int) -> EventRegistration | None:
        """Find an event registration by its associated event ID.

        Args:
            event_id: The event ID to find registration for

        Returns:
            EventRegistration or None: The registration if found
        """
        return cls.query.filter_by(event_id=event_id).first()

    @classmethod
    def create_event_registration(
        cls,
        event_id: int,
        public: bool = False,
        reg_open: bool = False,
        reg_start_date: datetime | None = None,
        reg_end_date: datetime | None = None,
        commit: bool = True,
    ) -> EventRegistration:
        """Create and persist a new event registration.

        Args:
            event_id: Event ID
            public: Whether registration is public
            reg_open: Whether registration is open
            reg_start_date: Registration start date
            reg_end_date: Registration end date
            commit: Whether to commit immediately

        Returns:
            EventRegistration: The created instance
        """
        registration = cls(
            event_id=event_id,
            public=public,
            reg_open=reg_open,
            reg_start_date=reg_start_date,
            reg_end_date=reg_end_date,
        )

        db.session.add(registration)
        if commit:
            db.session.commit()
        return registration
