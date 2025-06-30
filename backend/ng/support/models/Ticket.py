"""
Defines the Ticket database model for support ticket metadata.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from CTFd.models import db

from ...core.utils import utc_now

if TYPE_CHECKING:
    from .TicketTag import TicketTag


class Ticket(db.Model):
    __tablename__ = "ng_tickets"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=utc_now)
    closed_timestamp = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=True, index=True)
    challenge_id = db.Column(db.Integer, nullable=True, index=True)  # Placeholder for future challenge integration TODO
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

    def __repr__(self):
        return f"<Ticket {self.id}: {self.subject}>"

    @hybrid_property
    def status(self):
        """Compute ticket status based on stored fields."""
        if self.closed_timestamp is not None:
            return "closed"
        elif self.muted:
            return "muted"
        else:
            return "open"

    @status.expression
    def status(cls):
        """SQLAlchemy expression for status property."""
        return db.case(
            (cls.closed_timestamp.isnot(None), "closed"),
            (cls.muted.is_(True), "muted"),
            else_="open",
        )

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize ticket for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized ticket data
        """
        data = {
            "id": self.id,
            "subject": self.subject,
            "author_id": self.author_id,
            "status": self.status,
            "opened_timestamp": self.opened_timestamp.isoformat() if self.opened_timestamp else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "event_id": self.event_id,
            "team_id": self.team_id,
            "challenge_id": self.challenge_id,
            "message_count": len(self.messages),
            "tags": [tag.name for tag in self.tags],
        }

        if include_admin_fields:
            data.update(
                {
                    "assigned_to": self.assigned_to,
                    "closed_timestamp": self.closed_timestamp.isoformat() if self.closed_timestamp else None,
                    "muted": self.muted,
                    "first_admin_response_timestamp": self.first_admin_response_timestamp.isoformat()
                    if self.first_admin_response_timestamp
                    else None,
                }
            )

        return data

    @classmethod
    def create(
        cls,
        subject: str,
        author_id: int,
        event_id: int | None = None,
        team_id: int | None = None,
        challenge_id: int | None = None,
        tags: list["TicketTag"] | None = None,
        commit: bool = True,
    ) -> "Ticket":
        """Create and persist a new ticket.

        Args:
            subject: Ticket subject line
            author_id: User ID creating the ticket
            event_id: Optional event association
            team_id: Optional team association
            challenge_id: Optional challenge association
            tags: Optional list of tags to attach
            commit: Whether to commit immediately

        Returns:
            Ticket: The created ticket instance
        """
        ticket = cls(
            subject=subject,
            author_id=author_id,
            event_id=event_id,
            team_id=team_id,
            challenge_id=challenge_id,
            opened_timestamp=utc_now(),
            last_updated=utc_now(),
        )

        if tags:
            ticket.tags.extend(tags)

        db.session.add(ticket)
        if commit:
            db.session.commit()
        return ticket

    def update_ticket(self, commit=True, **kwargs):
        """Update ticket properties and persist to database.

        Args:
            **kwargs: Ticket properties to update

        Returns:
            bool: True if successful
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.last_updated = utc_now()
        if commit:
            db.session.commit()
        return True

    def close_ticket(self, commit: bool = True) -> None:
        """Close the ticket by setting closed timestamp."""
        self.closed_timestamp = utc_now()
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def reopen_ticket(self, commit: bool = True) -> None:
        """Reopen a closed ticket."""
        self.closed_timestamp = None
        self.muted = False
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def mute_ticket(self, commit: bool = True) -> None:
        """Mute the ticket."""
        self.muted = True
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def unmute_ticket(self, commit: bool = True) -> None:
        """Unmute the ticket."""
        self.muted = False
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def assign_to_user(self, user_id: int, commit: bool = True) -> None:
        """Assign ticket to a user."""
        self.assigned_to = user_id
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def unassign(self, commit: bool = True) -> None:
        """Remove ticket assignment."""
        self.assigned_to = None
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def set_first_admin_response(self, timestamp: datetime = None, commit: bool = True) -> None:
        """Set the first admin response timestamp if not already set."""
        if self.first_admin_response_timestamp is None:
            self.first_admin_response_timestamp = timestamp or utc_now()
            if commit:
                db.session.commit()

    def add_tags(self, tags: list["TicketTag"], commit: bool = True) -> None:
        """Add tags to the ticket."""
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    def remove_tags(self, tags: list["TicketTag"], commit: bool = True) -> None:
        """Remove tags from the ticket."""
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
        self.last_updated = utc_now()
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, ticket_id: int) -> "Ticket" | None:
        """Find a ticket by ID.

        Args:
            ticket_id: The ticket ID to find

        Returns:
            Ticket or None: The ticket instance if found
        """
        return cls.query.get(ticket_id)

    @classmethod
    def find_by_author(cls, author_id: int) -> list["Ticket"]:
        """Find all tickets by a specific author.

        Args:
            author_id: The author's user ID

        Returns:
            List[Ticket]: List of tickets by the author
        """
        return cls.query.filter_by(author_id=author_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_by_assigned_user(cls, user_id: int) -> list["Ticket"]:
        """Find all tickets assigned to a user.

        Args:
            user_id: The assigned user's ID

        Returns:
            List[Ticket]: List of tickets assigned to the user
        """
        return cls.query.filter_by(assigned_to=user_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_open_tickets(cls) -> list["Ticket"]:
        """Find all open tickets."""
        return (
            cls.query.filter(cls.closed_timestamp.is_(None), cls.muted.is_(False))
            .order_by(cls.last_updated.desc())
            .all()
        )

    @classmethod
    def find_by_event(cls, event_id: int) -> list["Ticket"]:
        """Find all tickets for a specific event."""
        return cls.query.filter_by(event_id=event_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_by_team(cls, team_id: int) -> list["Ticket"]:
        """Find all tickets for a specific team."""
        return cls.query.filter_by(team_id=team_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_unassigned_open_tickets(cls) -> list["Ticket"]:
        """Find all open tickets that are not assigned."""
        return (
            cls.query.filter(
                cls.closed_timestamp.is_(None),
                cls.muted.is_(False),
                cls.assigned_to.is_(None),
            )
            .order_by(cls.opened_timestamp.asc())
            .all()
        )

    @classmethod
    def get_ticket_stats(cls) -> dict[str, Any]:
        """Get overall ticket statistics."""

        total = cls.query.count()
        open_count = cls.query.filter(cls.closed_timestamp.is_(None), cls.muted.is_(False)).count()
        closed_count = cls.query.filter(cls.closed_timestamp.isnot(None)).count()
        muted_count = cls.query.filter(cls.muted.is_(True)).count()
        unassigned_count = cls.query.filter(cls.closed_timestamp.is_(None), cls.assigned_to.is_(None)).count()

        # Calculate average response time
        tickets_with_response = cls.query.filter(cls.first_admin_response_timestamp.isnot(None)).all()

        if tickets_with_response:
            total_response_time = sum(
                (ticket.first_admin_response_timestamp - ticket.opened_timestamp).total_seconds()
                for ticket in tickets_with_response
            )
            avg_response_time_seconds = total_response_time / len(tickets_with_response)
            avg_response_time_hours = avg_response_time_seconds / 3600
            avg_response_time_hours = round(avg_response_time_hours, 2)
        else:
            avg_response_time_hours = None

        # Get tickets closed today
        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        tickets_closed_today = cls.query.filter(cls.closed_timestamp >= today_start).count()

        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "muted": muted_count,
            "unassigned": unassigned_count,
            "avg_response_time_hours": avg_response_time_hours,
            "closed_today": tickets_closed_today,
        }

    @classmethod
    def find_filtered_tickets(
        cls,
        user_id: int | None = None,
        status: str = "all",
        assigned_to: int | None = None,
        event_id: int | None = None,
        team_id: int | None = None,
        is_admin: bool = False,
    ) -> list["Ticket"]:
        """Find tickets based on filters and permissions.

        Args:
            user_id: Filter by ticket author (for non-admin users, this is enforced)
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
            query = query.filter(cls.closed_timestamp.is_(None), cls.muted.is_(False))
        elif status == "closed":
            query = query.filter(cls.closed_timestamp.isnot(None))
        elif status == "muted":
            query = query.filter(cls.muted.is_(True))

        # Additional filters (admin only)
        if is_admin:
            if assigned_to is not None:
                query = query.filter_by(assigned_to=assigned_to)
            if event_id is not None:
                query = query.filter_by(event_id=event_id)
            if team_id is not None:
                query = query.filter_by(team_id=team_id)

        return query.order_by(cls.last_updated.desc()).all()

    @classmethod
    def create_with_validation(
        cls,
        subject: str,
        author_id: int,
        event_id: int | None = None,
        team_id: int | None = None,
        challenge_id: int | None = None,
        tag_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """Create a ticket with validation of associations.

        Returns:
            dict: {"success": bool, "ticket": Ticket | None, "error": str | None}
        """
        try:
            if event_id:
                from ...event.models.Event import Event

                if not Event.find_by_id(event_id):
                    return {
                        "success": False,
                        "error": f"Event with ID {event_id} not found",
                    }

            if team_id:
                from ...team.models.Team import Team

                if not Team.find_by_id(team_id):
                    return {
                        "success": False,
                        "error": f"Team with ID {team_id} not found",
                    }

            tags = []
            if tag_ids:
                from .TicketTag import TicketTag

                for tag_id in tag_ids:
                    tag = TicketTag.find_by_id(tag_id)
                    if not tag:
                        return {
                            "success": False,
                            "error": f"Tag with ID {tag_id} not found",
                        }
                    tags.append(tag)

            ticket = cls.create(
                subject=subject,
                author_id=author_id,
                event_id=event_id,
                team_id=team_id,
                challenge_id=challenge_id,
                tags=tags,
                commit=True,
            )

            return {"success": True, "ticket": ticket, "error": None}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "ticket": None, "error": str(e)}

    def assign_to_user_with_validation(self, user_id: int) -> dict[str, Any]:
        """Assign ticket to a user with validation.

        Returns:
            dict: {"success": bool, "user_name": str | None, "error": str | None}
        """
        try:
            from CTFd.models import Users

            user = Users.query.get(user_id)
            if not user:
                return {"success": False, "error": f"User with ID {user_id} not found"}

            self.assign_to_user(user_id, commit=True)

            return {"success": True, "user_name": user.name, "error": None}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "user_name": None, "error": str(e)}

    def add_message_with_updates(self, text: str, author_id: int, is_admin: bool = False) -> dict[str, Any]:
        """Add a message and handle ticket state updates.

        Returns:
            dict: {"message": TicketMessage, "ticket_reopened": bool}
        """
        from .TicketMessage import TicketMessage

        ticket_reopened = False
        if self.status == "closed" and is_admin:
            self.reopen_ticket(commit=False)
            ticket_reopened = True

        message = TicketMessage.create(text=text, ticket_id=self.id, author_id=author_id, commit=False)

        if is_admin:
            self.set_first_admin_response(commit=False)

        self.last_updated = utc_now()

        db.session.commit()

        return {"message": message, "ticket_reopened": ticket_reopened}


# Junction table for many to many relationship between tickets and tags
ticket_tags_junction = db.Table(
    "ng_ticket_tags_junction",
    db.Column("ticket_id", db.Integer, db.ForeignKey("ng_tickets.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("ng_ticket_tags.id"), primary_key=True),
)
