"""
Defines the TicketMessage model for support ticket thread messages.
"""

from __future__ import annotations
from typing import Any, TypedDict

from CTFd.models import db, Users

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator


class SerializedTicketMessage(TypedDict):
    id: int
    text: str
    author_id: int
    author_name: str
    author_type: str
    created_at: str | None
    ticket_id: int


class TicketMessage(db.Model):
    __tablename__ = "ng_ticket_messages"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(config.TICKET_MESSAGE_MAX_LENGTH), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ng_tickets.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    ticket = db.relationship("Ticket", back_populates="messages")
    author = db.relationship("Users", backref="ticket_messages")

    def __repr__(self) -> str:
        return f"<TicketMessage {self.id} on Ticket {self.ticket_id}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate Ticket Message data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "text",
            config.TICKET_MESSAGE_MAX_LENGTH,
            required=True,
            friendly_name="Message text",
        )
        validator.validate_model_id(data, "ticket_id", "Ticket", required=True)
        validator.validate_model_id(data, "author_id", "Users", required=True)

        return validator.validate()

    def serialize(
        self,
        include_admin_fields: bool = False,
        author_cache: dict[int, Any] | None = None,
    ) -> SerializedTicketMessage:
        """
        Serialize message for API response.

        Args:
            include_admin_fields: Whether to include admin only fields
            author_cache: Optional cache of author data to avoid N+1 queries

        Returns:
            dict: Serialized message data
        """
        # Get author info from cache or query if not cached
        if author_cache and self.author_id in author_cache:
            author_info = author_cache[self.author_id]
            author_name = author_info["name"]
            author_type = author_info["type"]
        else:
            # Fallback to query
            author = Users.query.get(self.author_id)
            author_name = author.name if author else f"User {self.author_id}"
            author_type = getattr(author, "type", "user") if author else "user"

        data = {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "author_name": author_name,
            "author_type": author_type,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "ticket_id": self.ticket_id,
        }

        return SerializedTicketMessage(**data)  # type: ignore[typeddict-item]

    @classmethod
    def create_message(cls, text: str, ticket_id: int, author_id: int, commit: bool = True) -> TicketMessage:
        """
        Create and persist a new ticket message with validation.

        Args:
            text: Message content (markdown supported)
            ticket_id: ID of the ticket this message belongs to
            author_id: User ID of the message author
            commit: Whether to commit immediately

        Returns:
            TicketMessage: The created message instance
        """

        data = {
            "text": text,
            "ticket_id": ticket_id,
            "author_id": author_id,
        }

        validated_data = cls.validate(data)

        message = cls(
            text=validated_data["text"],
            ticket_id=validated_data["ticket_id"],
            author_id=validated_data["author_id"],
        )

        db.session.add(message)
        if commit:
            db.session.commit()
        return message

    @classmethod
    def find_by_id(cls, message_id: int) -> TicketMessage | None:
        """
        Find a message by ID.
        """
        return cls.query.get(message_id)

    @classmethod
    def delete_by_ticket(cls, ticket_id: int, commit: bool = True) -> int:
        """
        Delete all messages for a ticket.
        """
        count = cls.query.filter_by(ticket_id=ticket_id).delete()
        if commit:
            db.session.commit()
        return count
