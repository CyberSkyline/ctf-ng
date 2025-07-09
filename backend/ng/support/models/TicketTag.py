"""
Defines the TicketTag model for categorizing support tickets.
"""

from __future__ import annotations
from typing import Any

from CTFd.models import db


class TicketTag(db.Model):
    __tablename__ = "ng_ticket_tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(7), nullable=True)
    description = db.Column(db.String(200), nullable=True)

    tickets = db.relationship("Ticket", secondary="ng_ticket_tags_junction", back_populates="tags")

    def __repr__(self):
        return f"<TicketTag {self.name}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize tag for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

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

    # TODO - create validate function

    @classmethod
    def create(
        cls,
        name: str,
        color: str | None = None,
        description: str | None = None,
        commit: bool = True,
    ) -> TicketTag:
        """Create and persist a new ticket tag.

        Args:
            name: Tag name
            color: Optional hex color code
            description: Optional tag description
            commit: Whether to commit immediately

        Returns:
            TicketTag: The created tag instance
        """
        # TODO - call validate
        tag = cls(name=name, color=color, description=description)

        db.session.add(tag)
        if commit:
            db.session.commit()
        return tag

    # TODO - should not have a return val
    def update_tag(self, **kwargs) -> bool:
        """Update tag properties and persist to database.

        Args:
            **kwargs: Tag properties to update

        Returns:
            bool: True if successful
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        db.session.commit()
        return True

    def delete_tag(self) -> None:
        """Delete this tag from the database."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, tag_id: int) -> TicketTag | None:
        """Find a tag by ID.

        Args:
            tag_id: The tag ID to find

        Returns:
            TicketTag or None: The tag instance if found
        """
        return cls.query.get(tag_id)

    @classmethod
    def find_by_name(cls, name: str) -> TicketTag | None:
        """Find a tag by name.

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
        # Lazy import to prevent circular dependencies (needed)
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
        return cls.query.filter(cls.name.ilike(f"%{query}%")).order_by(cls.name.asc()).all()
