"""
Defines the TicketTag model for categorizing support tickets.
"""

from __future__ import annotations
from typing import Any, TypedDict

from CTFd.models import db
from sqlalchemy.exc import IntegrityError

from ... import config
from ...core.utils.validator import BaseValidator
from ...core.exceptions import ConflictError


class SerializedTicketTag(TypedDict):
    id: int
    name: str
    color: str | None
    description: str | None
    ticket_count: int


class TicketTag(db.Model):
    __tablename__ = "ng_ticket_tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.TICKET_TAG_NAME_MAX_LENGTH), nullable=False, unique=True)
    color = db.Column(db.String(config.TICKET_TAG_COLOR_MAX_LENGTH), nullable=True)
    description = db.Column(db.String(config.TICKET_TAG_DESCRIPTION_MAX_LENGTH), nullable=True)

    tickets = db.relationship("Ticket", secondary="ng_ticket_tags_junction", back_populates="tags")

    def __repr__(self) -> str:
        return f"<TicketTag {self.name}>"

    @classmethod
    def validate(cls, data: dict[str, Any], current_instance: TicketTag | None = None) -> dict[str, Any]:
        """
        Validate Ticket Tag data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            min_length=config.TICKET_TAG_NAME_MIN_LENGTH,
            max_length=config.TICKET_TAG_NAME_MAX_LENGTH,
            required=not bool(current_instance),
            friendly_name="Tag name",
        )

        validator.validate_string(
            data,
            "color",
            max_length=config.TICKET_TAG_COLOR_MAX_LENGTH,
            required=False,
            friendly_name="Tag color",
        )

        validator.validate_string(
            data,
            "description",
            max_length=config.TICKET_TAG_DESCRIPTION_MAX_LENGTH,
            required=False,
            friendly_name="Tag description",
        )

        return validator.validate()

    def serialize(self, include_admin_fields: bool = False) -> SerializedTicketTag:
        """
        Serialize tag for API response.

        Args:
            include_admin_fields: Not used for tags, but kept for API consistency
        """
        data = {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "ticket_count": len(self.tickets),
        }

        return SerializedTicketTag(**data)

    @classmethod
    def create_tag(
        cls,
        name: str,
        color: str | None = None,
        description: str | None = None,
        commit: bool = True,
    ) -> TicketTag:
        """
        Create and persist a new ticket tag with validation.

        Args:
            name: Tag name
            color: Optional hex color code
            description: Optional tag description
            commit: Whether to commit immediately

        Returns:
            TicketTag: The created tag instance
        """

        validated_data = cls.validate(
            {
                "name": name,
                "color": color,
                "description": description,
            }
        )

        tag = cls(
            name=validated_data["name"],
            color=validated_data.get("color"),
            description=validated_data.get("description"),
        )

        db.session.add(tag)
        if commit:
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                if "UNIQUE constraint failed" in str(e) or "unique" in str(e).lower():
                    raise ConflictError(f"Tag name '{name}' already exists") from e
                raise
        return tag

    def update_tag(self, commit: bool = True, **kwargs) -> None:
        """
        Update tag properties and persist to database.

        Args:
            commit: Whether to commit immediately
            **kwargs: Tag properties to update
        """

        update_data = {}
        if "name" in kwargs:
            update_data["name"] = kwargs["name"]
        if "color" in kwargs:
            update_data["color"] = kwargs["color"]
        if "description" in kwargs:
            update_data["description"] = kwargs["description"]

        if update_data:
            validated_data = self.validate(update_data, current_instance=self)

            for key, value in validated_data.items():
                setattr(self, key, value)

        if commit:
            db.session.commit()

    def delete_tag(self, commit: bool = True) -> None:
        """
        Delete this tag from the database.
        """
        db.session.delete(self)
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, tag_id: int) -> TicketTag | None:
        """
        Find a tag by ID.
        """
        return cls.query.get(tag_id)

    @classmethod
    def find_by_name(cls, name: str) -> TicketTag | None:
        """
        Find a tag by name.
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all_tags(cls) -> list[TicketTag]:
        """
        Get all tags ordered by name.
        """
        return cls.query.order_by(cls.name.asc()).all()
