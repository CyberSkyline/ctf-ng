"""
Defines the TeamMember model, link between users, teams, and events.
"""

from __future__ import annotations
from typing import Any

from CTFd.models import db

from ...core.utils import utc_now
from .enums import TeamRole


class TeamMember(db.Model):
    __tablename__ = "ng_team_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    role = db.Column(db.Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", name="uq_user_event"),
        db.Index("ix_ng_team_members_team_role", "team_id", "role"),
    )  # Users can only be in one team per event

    user = db.relationship("User", back_populates="team_members")
    team = db.relationship("Team", back_populates="members")
    event = db.relationship("Event")

    def __repr__(self):
        return f"<TeamMember user={self.user_id} team={self.team_id} event={self.event_id}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        """Serialize team member for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized team member data
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "event_id": self.event_id,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "role": self.role.value,
        }

        return data

    @classmethod
    def create_team_member(
        cls,
        user_id,
        team_id,
        event_id,
        role=TeamRole.MEMBER,
        joined_at=None,
        commit=True,
    ):
        """Create and persist a new team member to the database.

        Args:
            user_id (int): User ID
            team_id (int): Team ID
            event_id (int): Event ID
            role (TeamRole, optional): Member role
            joined_at (datetime, optional): Join timestamp
            commit (bool, optional): Whether to commit immediately. Defaults to True.

        Returns:
            TeamMember: The created team member instance
        """
        if joined_at is None:
            joined_at = utc_now()

        team_member = cls(
            user_id=user_id,
            team_id=team_id,
            event_id=event_id,
            joined_at=joined_at,
            role=role,
        )

        db.session.add(team_member)
        if commit:
            db.session.commit()
        return team_member

    def remove_team_member(self, commit=True):
        """Remove this team member from the database."""
        db.session.delete(self)
        if commit:
            db.session.commit()

    def update_role(self, new_role, commit=True):
        """Update member role and persist to database."""
        self.role = new_role
        if commit:
            db.session.commit()

    @classmethod
    def find_by_user_and_event(cls, user_id: int, event_id: int):
        """Find a team member by user and event.

        Args:
            user_id (int): The user ID to find
            event_id (int): The event ID to search within

        Returns:
            TeamMember or None: The team member instance if found, None otherwise
        """
        return cls.query.filter_by(user_id=user_id, event_id=event_id).first()

    @classmethod
    def count_by_event(cls, event_id: int) -> int:
        """Get the count of team members in a specific event.

        Args:
            event_id (int): The event ID to count team members for

        Returns:
            int: Number of team members in the event
        """
        return cls.query.filter_by(event_id=event_id).count()

    @classmethod
    def find_captain_by_team(cls, team_id: int):
        """Find the captain of a team.

        Args:
            team_id (int): The team ID to find captain for

        Returns:
            TeamMember or None: The captain team member if found, None otherwise
        """
        return cls.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()

    @classmethod
    def find_captain_by_team_and_user(cls, team_id: int, user_id: int):
        """Find a captain by team and user (for authorization checks).

        Args:
            team_id (int): The team ID to check
            user_id (int): The user ID to check

        Returns:
            TeamMember or None: The captain team member if found, None otherwise
        """
        return cls.query.filter_by(team_id=team_id, user_id=user_id, role=TeamRole.CAPTAIN).first()

    @classmethod
    def find_by_user_and_team(cls, user_id: int, team_id: int):
        """Find a team member by user and team.

        Args:
            user_id (int): The user ID to find
            team_id (int): The team ID to search within

        Returns:
            TeamMember or None: The team member instance if found, None otherwise
        """
        return cls.query.filter_by(user_id=user_id, team_id=team_id).first()

    @classmethod
    def find_all_by_team(cls, team_id: int) -> list["TeamMember"]:
        """Find all team members in a team.

        Args:
            team_id (int): The team ID to search within

        Returns:
            list[TeamMember]: List of team members in the team
        """
        return cls.query.filter_by(team_id=team_id).all()

    @classmethod
    def count_other_members_in_team(cls, team_id: int, exclude_member_id: int) -> int:
        """Count other members in a team excluding a specific member.

        Args:
            team_id (int): The team ID to count in
            exclude_member_id (int): The team member ID to exclude

        Returns:
            int: Count of other members
        """
        return cls.query.filter(cls.team_id == team_id, cls.id != exclude_member_id).count()

    @classmethod
    def find_remaining_members_for_captain_removal(cls, team_id: int, captain_id: int) -> list["TeamMember"]:
        """Find remaining members when removing a captain (for auto-promotion).

        Args:
            team_id (int): The team ID to search in
            captain_id (int): The captain member ID being removed

        Returns:
            list[TeamMember]: List of remaining members ordered by join date
        """
        return (
            cls.query.filter(
                cls.team_id == team_id,
                cls.id != captain_id,
                cls.role == TeamRole.MEMBER,
            )
            .order_by(cls.joined_at.asc())
            .all()
        )

    @classmethod
    def get_total_count(cls) -> int:
        """Get the total count of all team members.

        Returns:
            int: Total number of team members
        """
        return cls.query.count()

    @classmethod
    def delete_by_event(cls, event_id: int) -> int:
        """Delete all team members in a specific event.

        Args:
            event_id (int): The event ID to delete team members from

        Returns:
            int: Number of team members deleted
        """
        count = cls.query.filter_by(event_id=event_id).delete()
        db.session.commit()
        return count

    @classmethod
    def find_all_by_team_ordered_by_join_date(cls, team_id: int) -> list["TeamMember"]:
        """Find all team members in a team ordered by join date (oldest first).

        Args:
            team_id (int): The team ID to search within

        Returns:
            list[TeamMember]: List of team members ordered by join date
        """
        return cls.query.filter_by(team_id=team_id).order_by(cls.joined_at.asc()).all()

    @classmethod
    def transfer_captain_role(cls, team_id: int, old_captain_id: int, new_captain_id: int) -> bool:
        """Transfer captain role in a single transaction."""
        try:
            old_captain = cls.query.get(old_captain_id)
            new_captain = cls.query.get(new_captain_id)

            if old_captain:
                old_captain.role = TeamRole.MEMBER
            new_captain.role = TeamRole.CAPTAIN

            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def delete_all(cls) -> None:
        """Delete all team members from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
