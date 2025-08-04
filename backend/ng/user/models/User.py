"""
Defines the User extension model.
"""

from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import db
from sqlalchemy.ext.associationproxy import association_proxy

from ...permissions.models.UserRole import UserRole


class SerializedUser(TypedDict):
    id: int
    name: str
    email: str
    role: str
    registered_at: str
    oauth_id: str


class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table

    ctfd_user = db.relationship(
        "Users",
        backref=db.backref("ng_users", uselist=False, cascade="all, delete-orphan"),
        lazy="joined",
        foreign_keys=[id],
    )

    team_members = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    user_roles = db.relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    roles = association_proxy("user_roles", "role", creator=lambda role: UserRole(role=role))

    def __repr__(self):
        return f"<NgUser id={self.id}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        if not self.ctfd_user:
            return {
                "id": self.id,
                "name": f"User {self.id} (Data Inconsistency)",
                "email": "",
                "role": "unknown",
                "registered_at": "",
            }

        if include_admin_fields:
            return {
                "id": self.id,
                "name": self.ctfd_user.name,
                "email": self.ctfd_user.email,
                "roles": [role.name for role in self.roles],
                "registered_at": self.ctfd_user.created.isoformat() + "Z",
            }
        return {
            "id": self.id,
            "name": self.ctfd_user.name,
            "email": self.ctfd_user.email,
            "registered_at": self.ctfd_user.created.isoformat() + "Z",
            }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        # TODO - implement
        return data

    @classmethod
    def create_user(cls, user_id, commit=True):
        """Create and persist a new user extension to the database.

        Args:
            user_id (int): CTFd user ID to link to
            commit (bool, optional): Whether to commit immediately

        Returns:
            User: The created user instance
        """
        user = cls(id=user_id)
        db.session.add(user)
        if commit:
            db.session.commit()
        return user

    def get_events(self):
        """Get all events the user is registered in.

        Returns:
            list: List of events the user is registered in
        """
        from ...event.models.Event import Event
        from ...team.models.TeamMember import TeamMember

        # Get all teams the user is a member of
        team_members = TeamMember.query.filter_by(user_id=self.id).all()
        event_ids = [tm.event_id for tm in team_members]

        # Get all events for those teams
        events = Event.query.filter(Event.id.in_(event_ids)).all()
        return events

    def get_teams(self):
        """Get all teams the user is a member of.

        Returns:
            list: List of teams the user is a member of
        """

        # Get all team members for this user
        return [tm.team for tm in self.team_members]

    @classmethod
    def find_by_id(cls, user_id: int):
        """Find a user by ID.

        Args:
            user_id (int): The user ID to find

        Returns:
            User or None: The user instance if found, None otherwise
        """
        return cls.query.get(user_id)

    @classmethod
    def find_or_create_by_ctfd_id(cls, ctfd_user_id: int, commit: bool = True) -> User:
        """Find or create a user by CTFd user ID.

        Args:
            ctfd_user_id (int): The CTFd user ID to find or create
            commit (bool, optional): Whether to commit immediately

        Returns:
            User: The found or created user instance
        """
        user = cls.query.get(ctfd_user_id)
        if not user:
            user = cls.create_user(ctfd_user_id, commit=commit)
        return user

    @classmethod
    def get_all_users(cls):
        """Gets all users with their basic details."""

        return cls.query.all()

    @classmethod
    def check_can_join_team_in_event(cls, user_id: int, event_id: int) -> bool:
        """Checks if a user can join a team in the event.

        Args:
            user_id (int): The user ID.
            event_id (int): The event ID to check eligibility for.

        Returns:
            bool: True if user can join, False if already in a team.
        """
        from ...team.models.TeamMember import TeamMember

        existing_team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()
        return existing_team_member is None

    def get_permissions(self) -> list[str]:
        """Get all permissions for the user by aggregating from roles.

        Returns:
            list[str]: List of permission names assigned to the user
        """
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)

    @classmethod
    def delete_all(cls) -> None:
        """Delete all user extensions from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete(self) -> None:
        """Delete the user extension from the database."""
        db.session.delete(self)
        db.session.commit()


    def update(self, **kwargs) -> None:
        """Update user fields with provided keyword arguments.

        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.ctfd_user, key):
                setattr(self.ctfd_user, key, value)
        db.session.commit()
