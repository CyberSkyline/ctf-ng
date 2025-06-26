"""
/backend/ng/support/models/Ticket.py
Defines the Ticket database model for support ticket metadata.
"""

from CTFd.models import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from typing import Any, Optional, List
from ... import config


class Ticket(db.Model):
    __tablename__ = "ng_tickets"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    opened_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    closed_timestamp = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=True, index=True)
    challenge_id = db.Column(db.Integer, nullable=True, index=True)  # Placeholder for future challenge integration TODO
    muted = db.Column(db.Boolean, default=False, nullable=False)
    first_admin_response_timestamp = db.Column(db.DateTime, nullable=True)

    # Relationships
    messages = db.relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
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
            else_="open"
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
            "tags": [tag.name for tag in self.tags]
        }
        
        if include_admin_fields:
            data.update({
                "assigned_to": self.assigned_to,
                "closed_timestamp": self.closed_timestamp.isoformat() if self.closed_timestamp else None,
                "muted": self.muted,
                "first_admin_response_timestamp": self.first_admin_response_timestamp.isoformat() if self.first_admin_response_timestamp else None
            })
            
        return data

    @classmethod
    def create(cls, subject: str, author_id: int, event_id: Optional[int] = None, 
               team_id: Optional[int] = None, challenge_id: Optional[int] = None,
               tags: Optional[List['TicketTag']] = None, commit: bool = True) -> 'Ticket':
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
            opened_timestamp=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        if tags:
            ticket.tags.extend(tags)
            
        db.session.add(ticket)
        if commit:
            db.session.commit()
        return ticket

    def update_ticket(self, **kwargs) -> bool:
        """Update ticket properties and persist to database.
        
        Args:
            **kwargs: Ticket properties to update
            
        Returns:
            bool: True if successful
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.last_updated = datetime.utcnow()
        db.session.commit()
        return True

    def close_ticket(self, commit: bool = True) -> None:
        """Close the ticket by setting closed timestamp."""
        self.closed_timestamp = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def reopen_ticket(self, commit: bool = True) -> None:
        """Reopen a closed ticket."""
        self.closed_timestamp = None
        self.muted = False
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def mute_ticket(self, commit: bool = True) -> None:
        """Mute the ticket."""
        self.muted = True
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def unmute_ticket(self, commit: bool = True) -> None:
        """Unmute the ticket."""
        self.muted = False
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def assign_to_user(self, user_id: int, commit: bool = True) -> None:
        """Assign ticket to a user."""
        self.assigned_to = user_id
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def unassign(self, commit: bool = True) -> None:
        """Remove ticket assignment."""
        self.assigned_to = None
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def set_first_admin_response(self, timestamp: datetime = None, commit: bool = True) -> None:
        """Set the first admin response timestamp if not already set."""
        if self.first_admin_response_timestamp is None:
            self.first_admin_response_timestamp = timestamp or datetime.utcnow()
            if commit:
                db.session.commit()

    def add_tags(self, tags: List['TicketTag'], commit: bool = True) -> None:
        """Add tags to the ticket."""
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    def remove_tags(self, tags: List['TicketTag'], commit: bool = True) -> None:
        """Remove tags from the ticket."""
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
        self.last_updated = datetime.utcnow()
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, ticket_id: int) -> Optional['Ticket']:
        """Find a ticket by ID.
        
        Args:
            ticket_id: The ticket ID to find
            
        Returns:
            Ticket or None: The ticket instance if found
        """
        return cls.query.get(ticket_id)

    @classmethod
    def find_by_author(cls, author_id: int) -> List['Ticket']:
        """Find all tickets by a specific author.
        
        Args:
            author_id: The author's user ID
            
        Returns:
            List[Ticket]: List of tickets by the author
        """
        return cls.query.filter_by(author_id=author_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_by_assigned_user(cls, user_id: int) -> List['Ticket']:
        """Find all tickets assigned to a user.
        
        Args:
            user_id: The assigned user's ID
            
        Returns:
            List[Ticket]: List of tickets assigned to the user
        """
        return cls.query.filter_by(assigned_to=user_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_open_tickets(cls) -> List['Ticket']:
        """Find all open tickets."""
        return cls.query.filter(
            cls.closed_timestamp.is_(None),
            cls.muted.is_(False)
        ).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_by_event(cls, event_id: int) -> List['Ticket']:
        """Find all tickets for a specific event."""
        return cls.query.filter_by(event_id=event_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_by_team(cls, team_id: int) -> List['Ticket']:
        """Find all tickets for a specific team."""
        return cls.query.filter_by(team_id=team_id).order_by(cls.last_updated.desc()).all()

    @classmethod
    def find_unassigned_open_tickets(cls) -> List['Ticket']:
        """Find all open tickets that are not assigned."""
        return cls.query.filter(
            cls.closed_timestamp.is_(None),
            cls.muted.is_(False),
            cls.assigned_to.is_(None)
        ).order_by(cls.opened_timestamp.asc()).all()

    @classmethod
    def get_ticket_stats(cls) -> dict[str, Any]:
        """Get overall ticket statistics."""
        total = cls.query.count()
        open_count = cls.query.filter(
            cls.closed_timestamp.is_(None),
            cls.muted.is_(False)
        ).count()
        closed_count = cls.query.filter(cls.closed_timestamp.isnot(None)).count()
        muted_count = cls.query.filter(cls.muted.is_(True)).count()
        unassigned_count = cls.query.filter(
            cls.closed_timestamp.is_(None),
            cls.assigned_to.is_(None)
        ).count()
        
        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "muted": muted_count,
            "unassigned": unassigned_count
        }


# Junction table for many-to-many relationship between tickets and tags TODO
ticket_tags_junction = db.Table('ng_ticket_tags_junction',
    db.Column('ticket_id', db.Integer, db.ForeignKey('ng_tickets.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('ng_ticket_tags.id'), primary_key=True)
)
