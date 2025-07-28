"""
Defines the Ticket database model for support ticket metadata.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from sqlalchemy.ext.hybrid import hybrid_property

from CTFd.models import db, Users

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator
from ...core.exceptions import NotFoundError


if TYPE_CHECKING:
    from .TicketTag import TicketTag
    from .TicketMessage import TicketMessage


class Ticket(db.Model):
    __tablename__ = "ng_tickets"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(config.TICKET_SUBJECT_MAX_LENGTH), nullable=False)
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    closed_timestamp = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(
        db.DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
    assigned_to = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True, index=True
    )
    event_id = db.Column(
        db.Integer, db.ForeignKey("ng_events.id"), nullable=True, index=True
    )
    team_id = db.Column(
        db.Integer, db.ForeignKey("ng_teams.id"), nullable=True, index=True
    )
    challenge_id = db.Column(db.Integer, nullable=True, index=True)
    muted = db.Column(db.Boolean, default=False, nullable=False)
    first_admin_response_timestamp = db.Column(db.DateTime, nullable=True)

    messages = db.relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.created_at",
    )
    tags = db.relationship(
        "TicketTag", secondary="ng_ticket_tags_junction", back_populates="tickets"
    )
    author = db.relationship(
        "Users", foreign_keys=[author_id], backref="authored_tickets"
    )
    assigned_user = db.relationship(
        "Users", foreign_keys=[assigned_to], backref="assigned_tickets"
    )
    event = db.relationship("Event", backref="tickets")
    team = db.relationship("Team", backref="tickets")

    def __repr__(self) -> str:
        return f"<Ticket {self.id}: {self.subject}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        validator = BaseValidator()

        validator.validate_string(
            data,
            "subject",
            config.TICKET_SUBJECT_MAX_LENGTH,
            required=True,
            friendly_name="Ticket subject",
        )
        validator.validate_model_id(data, "author_id", "Users", required=True)

        validator.validate_model_id(data, "event_id", "Event", required=False)
        validator.validate_model_id(data, "team_id", "Team", required=False)
        validator.validate_model_id(data, "challenge_id", "Challenge", required=False)
        validator.validate_model_id(data, "assigned_to", "Users", required=False)
        validator.validate_boolean(
            data,
            "muted",
            required=False,
            friendly_name="Muted status",
        )

        if "tag_ids" in data and data["tag_ids"] is not None:
            if not isinstance(data["tag_ids"], list):
                validator.errors["tag_ids"] = "Tag IDs must be a list of numbers"
            else:
                valid_tag_ids = []
                for idx, tag_id in enumerate(data["tag_ids"]):
                    if not isinstance(tag_id, int) or tag_id <= 0:
                        validator.errors[f"tag_ids[{idx}]"] = (
                            "Each tag ID must be a positive integer"
                        )
                    else:
                        valid_tag_ids.append(tag_id)

                if valid_tag_ids and not validator.errors:
                    # LAZY-IMPORT
                    from .TicketTag import TicketTag

                    requested_tags = TicketTag.query.filter(
                        TicketTag.id.in_(valid_tag_ids)
                    ).all()

                    if len(requested_tags) != len(valid_tag_ids):
                        found_ids = {tag.id for tag in requested_tags}
                        missing_ids = set(valid_tag_ids) - found_ids
                        validator.errors["tag_ids"] = f"Tag IDs not found: {missing_ids}"
                    else:
                        validator._add_parsed_data("tag_ids", valid_tag_ids)

        return validator.validate()

    @hybrid_property
    def status(self) -> str:
        """
        Status is only open/closed
        """
        if self.closed_timestamp is not None:
            return "closed"
        else:
            return "open"

    @status.expression
    def status(cls): # noqa: N805
        """
        SQLAlchemy expression for status property
        """
        return db.case(
            (cls.closed_timestamp.isnot(None), "closed"),
            else_="open",
        )

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize ticket for API response.

        Args:
            include_admin_fields: Whether to include admin only fields

        Returns:
            dict: Serialized ticket data
        """
        data = {
            "id": self.id,
            "subject": self.subject,
            "author_id": self.author_id,
            "status": self.status,
            "opened_timestamp": self.opened_timestamp.isoformat() + "Z",
            "last_updated": self.last_updated.isoformat() + "Z",
            "event_id": self.event_id,
            "team_id": self.team_id,
            "challenge_id": self.challenge_id,
            "message_count": len(self.messages),
            "tags": [tag.name for tag in self.tags],
        }

        if include_admin_fields:
            first_admin_response_timestamp = (
                self.first_admin_response_timestamp.isoformat() + "Z"
                if self.first_admin_response_timestamp
                else None
            )
            data.update(
                {
                    "assigned_to": self.assigned_to,
                    "closed_timestamp": self.closed_timestamp.isoformat() + "Z"
                    if self.closed_timestamp
                    else None,
                    "muted": self.muted,
                    "first_admin_response_timestamp": first_admin_response_timestamp,
                }
            )

        return data

    @classmethod
    def create_ticket(
        cls,
        subject: str,
        author_id: int,
        event_id: int | None = None,
        team_id: int | None = None,
        challenge_id: int | None = None,
        tag_ids: list[int] | None = None,
        commit: bool = True,
    ) -> Ticket:
        """
        Create and persist a new ticket with validation.

        Args:
            subject: Ticket subject line
            author_id: User ID creating the ticket
            event_id: Optional event association
            team_id: Optional team association
            challenge_id: Optional challenge association
            tag_ids: Optional list of tag IDs to attach
            commit: Whether to commit immediately

        Returns:
            Ticket: The created ticket instance
        """

        validated_data = cls.validate({
            "subject": subject,
            "author_id": author_id,
            "event_id": event_id,
            "team_id": team_id,
            "challenge_id": challenge_id,
            "tag_ids": tag_ids,
        })

        ticket = cls(
            subject=validated_data["subject"],
            author_id=validated_data["author_id"],
            event_id=validated_data.get("event_id"),
            team_id=validated_data.get("team_id"),
            challenge_id=validated_data.get("challenge_id"),
        )

        if validated_data.get("tag_ids"):
            # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
            from .TicketTag import TicketTag

            requested_tags = TicketTag.query.filter(
                TicketTag.id.in_(validated_data["tag_ids"])
            ).all()
            ticket.tags.extend(requested_tags)

        db.session.add(ticket)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        return ticket

    def update_ticket(self, commit: bool = True, **kwargs) -> None:
        """Update ticket properties and persist to database.

        Args:
            commit: Whether to commit immediately
            **kwargs: Ticket properties to update
        """

        allowed_to_update = {
            "subject",
            "event_id",
            "team_id",
            "challenge_id",
            "assigned_to",
            "muted",
        }

        update_data = {
            key: value for key, value in kwargs.items() if key in allowed_to_update
        }

        if not update_data:
            return

        validator = BaseValidator()

        if "subject" in update_data:
            validator.validate_string(
                update_data, "subject", config.TICKET_SUBJECT_MAX_LENGTH
            )

        if "event_id" in update_data:
            validator.validate_model_id(update_data, "event_id", "Event")

        if "team_id" in update_data:
            validator.validate_model_id(update_data, "team_id", "Team")

        if "assigned_to" in update_data:
            validator.validate_model_id(update_data, "assigned_to", "Users")

        if "muted" in update_data:
            validator.validate_boolean(update_data, "muted")

        parsed_data = validator.validate()

        for key, value in parsed_data.items():
            setattr(self, key, value)

        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def close_ticket(self, commit: bool = True) -> None:
        """
        Close the ticket by setting closed timestamp.
        """
        self.closed_timestamp = utc_now()
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def reopen_ticket(self, commit: bool = True) -> None:
        """
        Reopen a closed ticket.
        """
        self.closed_timestamp = None
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def toggle_mute(self, muted: bool, commit: bool = True) -> None:
        """
        Toggle the muted state of the ticket.
        """
        self.muted = muted
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def assign_to_user(self, user_id: int, commit: bool = True) -> None:
        """Assign ticket to a user with validation.

        Args:
            user_id: The user ID to assign to
            commit: Whether to commit immediately
        """
        user = Users.query.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        self.assigned_to = user_id
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def unassign(self, commit: bool = True) -> None:
        """
        Remove ticket assignment.
        """
        self.assigned_to = None
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def add_tags(self, tags: list[TicketTag], commit: bool = True) -> None:
        """
        Add tags to the ticket.
        """
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def remove_tags(self, tags: list[TicketTag], commit: bool = True) -> None:
        """
        Remove tags from the ticket.
        """
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, ticket_id: int) -> Ticket | None:
        """Find a ticket by ID.

        Args:
            ticket_id: The ticket ID to find

        Returns:
            Ticket or None: The ticket instance if found
        """
        return cls.query.get(ticket_id)

    @classmethod
    def find_filtered_tickets(
        cls,
        user_id: int | None = None,
        status: str = "all",
        assigned_to: int | None = None,
        event_id: int | None = None,
        team_id: int | None = None,
        is_admin: bool = False,
    ) -> list[Ticket]:
        """
        Find tickets based on filters and permissions.

        Args:
            user_id: Filter by ticket author
            status: Filter by status (open, closed, muted, all)
            assigned_to: Filter by assigned user ID (admin only)
            event_id: Filter by event ID (admin only)
            team_id: Filter by team ID (admin only)
            is_admin: Whether the requesting user is an admin

        Returns:
            list[Ticket]: List of filtered tickets
        """
        query = cls.query

        if not is_admin and user_id:
            query = query.filter_by(author_id=user_id)
        elif user_id and is_admin:
            query = query.filter_by(author_id=user_id)

        if status == "open":
            query = query.filter(cls.closed_timestamp.is_(None))
        elif status == "closed":
            query = query.filter(cls.closed_timestamp.isnot(None))
        # Additional filters (admin only)
        if is_admin:
            if assigned_to is not None:
                query = query.filter_by(assigned_to=assigned_to)
            if event_id is not None:
                query = query.filter_by(event_id=event_id)
            if team_id is not None:
                query = query.filter_by(team_id=team_id)

        return query.order_by(cls.last_updated.desc()).all()

    def add_message(
        self, text: str, author_id: int, is_admin: bool = False, commit: bool = True
    ) -> None:
        """Add a message to the ticket and handle state updates.

        Args:
            text: Message content
            author_id: ID of the message author
            is_admin: Whether the author is an admin
            commit: Whether to commit immediately
        """
         # LAZY-IMPORT
        from .TicketMessage import TicketMessage

        if self.status == "closed" and is_admin:
            self.reopen_ticket(commit=False)

        TicketMessage.create_message(
            text=text, ticket_id=self.id, author_id=author_id, commit=False
        )

        if is_admin and self.first_admin_response_timestamp is None:
            self.first_admin_response_timestamp = utc_now()

        self.last_updated = utc_now()

        if commit:
            db.session.commit()

    def get_messages(self) -> list[TicketMessage]:
        """Get all messages for this ticket ordered by creation time.

        Returns:
            list[TicketMessage]: List of messages ordered by creation time
        """
        return self.messages

    def get_messages_with_authors(self) -> tuple[list[TicketMessage], dict[int, Any]]:
        """Get all messages for this ticket with author data efficiently loaded.

        Returns:
            tuple: (messages, author_cache) where author_cache maps author_id to author info
        """
        messages = self.messages
        author_ids = list(set(msg.author_id for msg in messages))

        authors = (
            Users.query.filter(Users.id.in_(author_ids)).all() if author_ids else []
        )

        # Author Cache
        author_cache = {
            author.id: {"name": author.name, "type": getattr(author, "type", "user")}
            for author in authors
        }
        return messages, author_cache


# Junction table for many to many relationship between tickets and tags
ticket_tags_junction = db.Table(
    "ng_ticket_tags_junction",
    db.Column(
        "ticket_id", db.Integer, db.ForeignKey("ng_tickets.id"), primary_key=True
    ),
    db.Column(
        "tag_id", db.Integer, db.ForeignKey("ng_ticket_tags.id"), primary_key=True
    ),
)
