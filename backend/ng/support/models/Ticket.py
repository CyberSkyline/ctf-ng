"""
Defines the Ticket database model for support ticket metadata.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING, TypedDict, NotRequired
from sqlalchemy.ext.hybrid import hybrid_property

from CTFd.models import db, Users

from ... import config
from ...core.utils import utc_now
from ...core.utils.validator import BaseValidator
from ...core.exceptions import NotFoundError, BusinessLogicError


if TYPE_CHECKING:
    from .TicketMessage import TicketMessage


class SerializedTicket(TypedDict):
    id: int
    subject: str
    author_id: int
    status: str
    opened_timestamp: str
    last_updated: str
    event_id: int | None
    team_id: int | None
    challenge_id: int | None
    message_count: int
    # Name enrichment fields
    event_name: NotRequired[str | None]
    team_name: NotRequired[str | None]
    challenge_name: NotRequired[str | None]
    author_name: NotRequired[str]
    # Admin-only fields
    assigned_to: NotRequired[int | None]
    closed_timestamp: NotRequired[str | None]
    muted: NotRequired[bool]
    first_admin_response_timestamp: NotRequired[str | None]
    tags: NotRequired[list[dict[str, str | int | None]]]
    # Admin name enrichment fields
    assigned_to_name: NotRequired[str | None]


class Ticket(db.Model):
    __tablename__ = "ng_tickets"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(config.TICKET_SUBJECT_MAX_LENGTH), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    closed_timestamp = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=True, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=True, index=True)
    muted = db.Column(db.Boolean, default=False, nullable=False)
    first_admin_response_timestamp = db.Column(db.DateTime, nullable=True)

    messages = db.relationship(
        "TicketMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.created_at",
    )
    tags = db.relationship("TicketTag", secondary="ng_ticket_tags_junction", back_populates="tickets")
    author = db.relationship("Users", foreign_keys=[author_id], backref="authored_tickets")
    assigned_user = db.relationship("Users", foreign_keys=[assigned_to], backref="assigned_tickets")
    event = db.relationship("Event", backref="tickets")
    team = db.relationship("Team", backref="tickets")
    challenge = db.relationship("Challenge")

    def __repr__(self) -> str:
        return f"<Ticket {self.id}: {self.subject}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate Ticket data. Raises ValidationError on failure
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "subject",
            min_length=config.TICKET_SUBJECT_MIN_LENGTH,
            max_length=config.TICKET_SUBJECT_MAX_LENGTH,
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

        return validator.validate()

    @hybrid_property
    def status(self) -> str:
        """
        Status is only open/closed
        """
        if self.closed_timestamp is not None:
            return "closed"
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

    def serialize(self, include_admin_fields: bool = False) -> SerializedTicket:
        """
        Serialize ticket for API response.

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
        }

        if self.event_id and self.event:
            data["event_name"] = self.event.name
        if self.team_id and self.team:
            data["team_name"] = self.team.name
        if self.challenge_id and self.challenge:
            data["challenge_name"] = self.challenge.name
        if self.author:
            data["author_name"] = self.author.name

        if include_admin_fields:
            first_admin_response_timestamp = (
                self.first_admin_response_timestamp.isoformat() + "Z" if self.first_admin_response_timestamp else None
            )
            data.update(
                {
                    "assigned_to": self.assigned_to,
                    "closed_timestamp": self.closed_timestamp.isoformat() + "Z" if self.closed_timestamp else None,
                    "muted": self.muted,
                    "first_admin_response_timestamp": first_admin_response_timestamp,
                    "tags": [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in self.tags],
                }
            )

            if self.assigned_to and self.assigned_user:
                data["assigned_to_name"] = self.assigned_user.name

        return SerializedTicket(**data)

    @classmethod
    def create_ticket(
        cls,
        subject: str,
        author_id: int,
        event_id: int | None = None,
        team_id: int | None = None,
        challenge_id: int | None = None,
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
            commit: Whether to commit immediately

        Returns:
            Ticket: The created ticket instance
        """

        validated_data = cls.validate(
            {
                "subject": subject,
                "author_id": author_id,
                "event_id": event_id,
                "team_id": team_id,
                "challenge_id": challenge_id,
            }
        )

        ticket = cls(
            subject=validated_data["subject"],
            author_id=validated_data["author_id"],
            event_id=validated_data.get("event_id"),
            team_id=validated_data.get("team_id"),
            challenge_id=validated_data.get("challenge_id"),
        )

        db.session.add(ticket)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        return ticket

    def update_subject(self, subject: str, commit: bool = True) -> None:
        """
        Update ticket subject
        """
        validator = BaseValidator()
        validator.validate_string(
            {"subject": subject},
            "subject",
            min_length=config.TICKET_SUBJECT_MIN_LENGTH,
            max_length=config.TICKET_SUBJECT_MAX_LENGTH,
            required=True,
            friendly_name="Ticket subject"
        )
        validated_data = validator.validate()

        self.subject = validated_data["subject"]
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def update_event_and_team(self, event_id: int | None, team_id: int | None, commit: bool = True) -> None:
        """
        Update ticket's event and team association
        Team must belong to the event if both are specified
        """
        validator = BaseValidator()

        if event_id is not None:
            validator.validate_model_id({"event_id": event_id}, "event_id", "Event", required=True)
        if team_id is not None:
            validator.validate_model_id({"team_id": team_id}, "team_id", "Team", required=True)

        validated_data = validator.validate()

        if event_id and team_id:
            # LAZY-IMPORT
            from ...team.models.Team import Team
            team = Team.find_by_id(team_id)
            if team and team.event_id != event_id:
                raise BusinessLogicError("Team does not belong to the specified event")

        self.event_id = validated_data.get("event_id")
        self.team_id = validated_data.get("team_id")

        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def update_challenge(self, challenge_id: int | None, commit: bool = True) -> None:
        """
        Update ticket's challenge association
        """
        validator = BaseValidator()
        validator.validate_model_id({"challenge_id": challenge_id}, "challenge_id", "Challenge", required=False)
        validated_data = validator.validate()

        self.challenge_id = validated_data.get("challenge_id")
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def set_tags(self, tag_ids: list[int], commit: bool = True) -> None:
        """
        Set ticket tags

        Args:
            tag_ids: List of tag IDs to set (empty list to clear all tags)
            commit: Whether to commit immediately
        """
        # LAZY-IMPORT
        from .TicketTag import TicketTag

        if tag_ids:
            tags = TicketTag.query.filter(TicketTag.id.in_(tag_ids)).all()
            if len(tags) != len(tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(tag_ids) - found_ids
                raise NotFoundError(f"Tag IDs not found: {missing_ids}")
        else:
            tags = []

        self.tags = tags
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
        """
        Assign ticket to a user with validation.
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

    @classmethod
    def find_by_id(cls, ticket_id: int) -> Ticket | None:
        """
        Find a ticket by ID.
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

    def add_message(self, text: str, author_id: int, is_admin: bool = False, commit: bool = True) -> None:
        """
        Add a message and handle related updates

        Args:
            text: Message content
            author_id: ID of the message author
            is_admin: Whether the author is an admin
            commit: Whether to commit immediately
        """
        # LAZY-IMPORT
        from .TicketMessage import TicketMessage

        TicketMessage.create_message(text=text, ticket_id=self.id, author_id=author_id, commit=False)

        if is_admin and self.first_admin_response_timestamp is None:
            self.first_admin_response_timestamp = utc_now()

        self.last_updated = utc_now()

        if commit:
            db.session.commit()

    def get_messages(self) -> list[TicketMessage]:
        """
        Get all messages for this ticket ordered by creation time.
        """
        return self.messages

    def get_messages_with_authors(self) -> tuple[list[TicketMessage], dict[int, Any]]:
        """
        Get all messages for this ticket with author data efficiently loaded.

        Returns:
            tuple: (messages, author_cache) where author_cache maps author_id to author info
        """
        messages = self.messages
        author_ids = list({msg.author_id for msg in messages})

        authors = Users.query.filter(Users.id.in_(author_ids)).all() if author_ids else []

        # Author Cache
        author_cache = {author.id: {"name": author.name, "type": getattr(author, "type", "user")} for author in authors}
        return messages, author_cache


# Junction table for many to many relationship between tickets and tags
ticket_tags_junction = db.Table(
    "ng_ticket_tags_junction",
    db.Column("ticket_id", db.Integer, db.ForeignKey("ng_tickets.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("ng_ticket_tags.id"), primary_key=True),
)
