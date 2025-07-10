"""
Defines the User extension model.
"""

from CTFd.models import db
from sqlalchemy.ext.associationproxy import association_proxy
from ...permissions.models.UserRole import UserRole
from typing import Any, TypedDict

class SerializedUser(TypedDict):
    id: int
    name: str
    email: str
    role: str
    registered_at: str

class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table

    ctfd_user = db.relationship(
        "Users",
        backref=db.backref("ng_user", uselist=False, cascade="all, delete-orphan"),
        lazy="joined",
        foreign_keys=[id],
    )

    team_members = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    user_roles = db.relationship("UserRole",back_populates="user",cascade="all, delete-orphan",)


    roles = association_proxy("user_roles","role",creator=lambda role: UserRole(role=role))

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
                "registered_at": self.ctfd_user.created.isoformat(),
            }
        else:
            return {
                "id": self.id,
                "name": self.ctfd_user.name,
                "email": self.ctfd_user.email,
                "registered_at": self.ctfd_user.created.isoformat(),
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
    def get_all_users(cls):
        """Gets all users with their basic details.
        """

        return cls.query().all()

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

    def delete_all(cls) -> None:
        """Delete all user extensions from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
