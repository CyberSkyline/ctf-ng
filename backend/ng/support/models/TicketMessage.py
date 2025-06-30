"""
Defines the TicketMessage model for support ticket thread messages.
"""

from __future__ import annotations
from typing import Any

from CTFd.models import db

from ...core.utils import utc_now


class TicketMessage(db.Model):
    __tablename__ = "ng_ticket_messages"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(4096), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ng_tickets.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    ticket = db.relationship("Ticket", back_populates="messages")
    author = db.relationship("Users", backref="ticket_messages")

    def __repr__(self):
        return f"<TicketMessage {self.id} on Ticket {self.ticket_id}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize message for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized message data
        """
        # Lazy import to prevent circular dependencies (needed)
        from CTFd.models import Users

        author = Users.query.get(self.author_id)
        author_name = author.name if author else f"User {self.author_id}"
        author_type = getattr(author, "type", "user") if author else "user"

        data = {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "author_name": author_name,
            "author_type": author_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ticket_id": self.ticket_id,
        }

        return data

    @classmethod
    def create(cls, text: str, ticket_id: int, author_id: int, commit: bool = True) -> "TicketMessage":
        """Create and persist a new ticket message.

        Args:
            text: Message content (markdown supported)
            ticket_id: ID of the ticket this message belongs to
            author_id: User ID of the message author
            commit: Whether to commit immediately

        Returns:
            TicketMessage: The created message instance
        """
        message = cls(text=text, ticket_id=ticket_id, author_id=author_id, created_at=utc_now())

        db.session.add(message)
        if commit:
            db.session.commit()
        return message

    @classmethod
    def find_by_id(cls, message_id: int) -> "TicketMessage" | None:
        """Find a message by ID.

        Args:
            message_id: The message ID to find

        Returns:
            TicketMessage or None: The message instance if found
        """
        return cls.query.get(message_id)

    @classmethod
    def find_by_ticket(cls, ticket_id: int) -> list["TicketMessage"]:
        """Find all messages for a specific ticket.

        Args:
            ticket_id: The ticket ID to get messages for

        Returns:
            list[TicketMessage]: List of messages ordered by creation time
        """
        return cls.query.filter_by(ticket_id=ticket_id).order_by(cls.created_at.asc()).all()

    @classmethod
    def find_by_author(cls, author_id: int) -> list["TicketMessage"]:
        """Find all messages by a specific author.

        Args:
            author_id: The author's user ID

        Returns:
            list[TicketMessage]: List of messages by the author
        """
        return cls.query.filter_by(author_id=author_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def count_by_ticket(cls, ticket_id: int) -> int:
        """Count messages in a ticket.

        Args:
            ticket_id: The ticket ID to count messages for

        Returns:
            int: Number of messages in the ticket
        """
        return cls.query.filter_by(ticket_id=ticket_id).count()

    @classmethod
    def get_first_admin_message(cls, ticket_id: int) -> "TicketMessage" | None:
        """Get the first message from an admin user in a ticket.

        Args:
            ticket_id: The ticket ID to check

        Returns:
            TicketMessage or None: The first admin message if exists
        """
        # Lazy import to prevent circular dependencies (needed)
        from CTFd.models import Users

        return (
            cls.query.join(Users)
            .filter(cls.ticket_id == ticket_id, Users.type == "admin")
            .order_by(cls.created_at.asc())
            .first()
        )

    @classmethod
    def delete_by_ticket(cls, ticket_id: int) -> int:
        """Delete all messages for a ticket.

        Args:
            ticket_id: The ticket ID to delete messages for

        Returns:
            int: Number of messages deleted
        """
        count = cls.query.filter_by(ticket_id=ticket_id).delete()
        db.session.commit()
        return count
