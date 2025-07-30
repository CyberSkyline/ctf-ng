"""
Defines the TicketTag model for categorizing support tickets.
"""

from __future__ import annotations
from typing import Any

from CTFd.models import db

from ... import config
from ...core.utils.validator import BaseValidator


class TicketTag(db.Model):
    __tablename__ = "ng_ticket_tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(config.TICKET_TAG_NAME_MAX_LENGTH), nullable=False, unique=True
    )
    color = db.Column(db.String(7), nullable=True)
    description = db.Column(
        db.String(config.TICKET_TAG_DESCRIPTION_MAX_LENGTH), nullable=True
    )

    tickets = db.relationship(
        "Ticket", secondary="ng_ticket_tags_junction", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<TicketTag {self.name}>"

    @classmethod
    def validate(
        cls, data: dict[str, Any], current_instance: TicketTag | None = None
    ) -> dict[str, Any]:
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            config.TICKET_TAG_NAME_MAX_LENGTH,
            required=not bool(current_instance),
            friendly_name="Tag name",
        )

        # Optional field
        if "color" in data and data["color"] is not None:
            color = data["color"]
            if not isinstance(color, str):
                validator.errors["color"] = "Color must be a string"
            elif not (len(color) == 7 and color.startswith("#")):
                validator.errors["color"] = (
                    "Color must be a valid hex code (e.g., #FF0000)"
                )
            else:
                validator._add_parsed_data("color", color)

        validator.validate_string(
            data,
            "description",
            config.TICKET_TAG_DESCRIPTION_MAX_LENGTH,
            required=False,
            friendly_name="Tag description",
        )

        if "name" in data and "name" not in validator.errors:
            existing = cls.query.filter_by(name=data["name"]).first()
            if existing:
                if not current_instance or existing.id != current_instance.id:
                    validator.errors["name"] = (
                        f"Tag name '{data['name']}' already exists"
                    )

        return validator.validate()

    def serialize(self) -> dict[str, Any]:
        """
        Serialize tag for API response.

        Returns:
            dict: Serialized tag data
        """
        data = {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "ticket_count": len(self.tickets),
        }

        return data

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

        validated_data = cls.validate({
            "name": name,
            "color": color,
            "description": description,
        })

        tag = cls(
            name=validated_data["name"],
            color=validated_data.get("color"),
            description=validated_data.get("description"),
        )

        db.session.add(tag)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
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

        Args:
            commit: Whether to commit immediately
        """
        db.session.delete(self)
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, tag_id: int) -> TicketTag | None:
        """
        Find a tag by ID.

        Args:
            tag_id: The tag ID to find

        Returns:
            TicketTag or None: The tag instance if found
        """
        return cls.query.get(tag_id)

    @classmethod
    def find_by_name(cls, name: str) -> TicketTag | None:
        """
        Find a tag by name.

        Args:
            name: The tag name to find

        Returns:
            TicketTag or None: The tag instance if found
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all_tags(cls) -> list[TicketTag]:
        """Get all tags ordered by name.

        Returns:
            list[TicketTag]: List of all tags
        """
        return cls.query.order_by(cls.name.asc()).all()

    @classmethod
    def get_popular_tags(cls, limit: int = 10) -> list[tuple[TicketTag, int]]:
        """Get most used tags.

        Args:
            limit: Maximum number of tags to return

        Returns:
            list[tuple[TicketTag, int]]: List of (tag, usage_count) tuples
        """
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from .Ticket import ticket_tags_junction

        popular = (
            db.session.query(
                cls,
                db.func.count(ticket_tags_junction.c.ticket_id).label("usage_count"),
            )
            .join(ticket_tags_junction, cls.id == ticket_tags_junction.c.tag_id)
            .group_by(cls.id)
            .order_by(db.func.count(ticket_tags_junction.c.ticket_id).desc())
            .limit(limit)
            .all()
        )

        return popular

    @classmethod
    def search_tags(cls, query: str) -> list[TicketTag]:
        """Search tags by name.

        Args:
            query: Search string

        Returns:
            list[TicketTag]: Matching tags
        """
        return (
            cls.query.filter(cls.name.ilike(f"%{query}%"))
            .order_by(cls.name.asc())
            .all()
        )
