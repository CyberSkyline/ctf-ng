"""
Defines the User extension model.
"""

from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import Users as CTFdUsers
from CTFd.models import db
from flask import g, has_request_context
from sqlalchemy import func, select
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from ...core.exceptions import BusinessLogicError
from ...core.utils.ag_grid import apply_filter_model, apply_sort_model, paginate
from ...core.utils.validator import BaseValidator
from ...permissions.models.UserRole import UserRole
from ...sponsors.models.Sponsor import Sponsor


class SerializedUser(TypedDict):
    id: int
    name: str
    email: str
    role: str
    registered_at: str
    oauth_id: str
    affiliation: str


class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table
    sponsor_id = db.Column(db.Integer, db.ForeignKey("ng_sponsors.id"), nullable=True)
    oauth_id = db.Column(db.String(256), nullable=True)

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

    affiliation = db.relationship(
        "Sponsor",
        back_populates="users",
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
                "affiliation": self.affiliation.serialize() if self.affiliation else None,
            }

        if include_admin_fields:
            return {
                "id": self.id,
                "name": self.ctfd_user.name,
                "email": self.ctfd_user.email,
                "roles": [role.name for role in self.roles],
                "registered_at": self.ctfd_user.created.isoformat() + "Z",
                "affiliation": self.affiliation.serialize(include_admin_fields=True) if self.affiliation else None,
                "banned": self.ctfd_user.banned,
                "is_sso": self.oauth_id is not None,
            }
        return {
            "id": self.id,
            "name": self.ctfd_user.name,
            "email": self.ctfd_user.email,
            "registered_at": self.ctfd_user.created.isoformat() + "Z",
            "affiliation": self.affiliation.serialize() if self.affiliation else None,
        }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate user data before creating or updating a user."""
        validator = BaseValidator()
        if "name" in data:
            validator.validate_string(data, "name", 128, required=True, friendly_name="Username")
        if "email" in data:
            validator.validate_string(data, "email", 128, required=True, friendly_name="Email")
        if "password" in data:
            validator.validate_string(data, "password", 128, required=True, friendly_name="Password", trim_whitespace=False)

        return validator.validate()

    @classmethod
    def validate_creation(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the data required to create a new user."""
        validator = BaseValidator()
        validator.validate_string(data, "name", 128, required=True, friendly_name="Username")
        validator.validate_string(data, "email", 128, required=True, friendly_name="Email")
        validator.validate_string(data, "password", 128, required=True, friendly_name="Password", trim_whitespace=False)

        return validator.validate()

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
        team_members = (TeamMember.query
            .filter_by(user_id=self.id)
            .options(
                joinedload(TeamMember.user),
                joinedload(TeamMember.team),
                joinedload(TeamMember.event)
            )
            .all()
        )
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
        return (cls.query
            .options(
                joinedload(cls.ctfd_user),
                joinedload(cls.user_roles).joinedload(UserRole.role)
            )
            .get(user_id)
        )

    @classmethod
    def find_or_create_by_ctfd_id(cls, ctfd_user_id: int, commit: bool = True) -> User:
        """Find or create a user by CTFd user ID.

        Args:
            ctfd_user_id (int): The CTFd user ID to find or create
            commit (bool, optional): Whether to commit immediately

        Returns:
            User: The found or created user instance
        """
        # Memoized per-request since the auth chain looks the same user up more than once
        cache = g.setdefault("_ng_user_by_ctfd_id", {}) if has_request_context() else {}
        if ctfd_user_id not in cache:
            user = (cls.query
                .options(
                    joinedload(cls.affiliation),
                    joinedload(cls.ctfd_user),
                    joinedload(cls.user_roles).joinedload(UserRole.role)
                )
                .get(ctfd_user_id)
            )
            cache[ctfd_user_id] = user or cls.create_user(ctfd_user_id, commit=commit)
        return cache[ctfd_user_id]

    @classmethod
    def find_paginated(cls, sort_model, filter_model, start_row, end_row) -> tuple[list[User], int]:
        """Fetch a page of users for the admin grid's server-side row model.

        Returns (users, total_count) with the ag-grid sort/filter model applied.
        """
        from ...permissions.models.Role import Role

        # Subquery to produce a comma-separated string of roles, consistent with previous client-side role filtering
        roles_summary = (
            select(func.group_concat(Role.name))
            .select_from(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(UserRole.user_id == cls.id)
            .scalar_subquery()
        )

        column_map = {
            "id": cls.id,
            "name": CTFdUsers.name,
            "email": CTFdUsers.email,
            "roles": roles_summary,
            "registered_at": CTFdUsers.created,
            "affiliation.name": Sponsor.name,
            "is_sso": cls.oauth_id.isnot(None),
            "banned": CTFdUsers.banned,
        }
        query = (cls.query
            .join(CTFdUsers, cls.id == CTFdUsers.id)
            .outerjoin(Sponsor, cls.sponsor_id == Sponsor.id)
            .options(
                contains_eager(cls.ctfd_user),
                contains_eager(cls.affiliation),
                selectinload(cls.user_roles).joinedload(UserRole.role),
            )
        )
        query = apply_filter_model(query, filter_model, column_map)
        query = apply_sort_model(query, sort_model, column_map, cls.id)
        return paginate(query, start_row, end_row)

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

    @classmethod
    def get_total_count(cls) -> int:
        """Get the total count of all users.

        Returns:
            int: Total number of users
        """
        return cls.query.count()

    def set_sponsor(self, sponsor, commit = True) -> None:
        """Set the user's sponsor affiliation.

        Args:
            sponsor (Sponsor): The sponsor to affiliate with
            commit (bool, optional): Whether to commit immediately
        """
        self.affiliation = sponsor
        if commit:
            db.session.commit()

    def get_sponsor(self):
        """Get the user's sponsor affiliation.

        Returns:
            Sponsor or None: The affiliated sponsor if exists, None otherwise
        """
        return self.affiliation


    def update(self, **kwargs) -> None:
        """Update user fields with provided keyword arguments.

        Args:
            **kwargs: Fields to update
        """
        # make sure we can't create expo account backdoors on an SSO user
        if "password" in kwargs and self.oauth_id is not None:
            raise BusinessLogicError("Cannot set a password for an SSO user", "password")

        for key, value in kwargs.items():
            if hasattr(self.ctfd_user, key):
                setattr(self.ctfd_user, key, value)
        db.session.commit()
