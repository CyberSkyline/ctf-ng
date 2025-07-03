"""
Defines the User extension model.
"""

from __future__ import annotations
from typing import Any

from CTFd.models import db
from sqlalchemy import func


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

    def __repr__(self):
        return f"<NgUser id={self.id}>"

    def serialize(self, include_admin_fields: bool = False) -> dict[str, Any]:
        if not self.ctfd_user:
            return {
                "id": self.id,
                "name": f"User {self.id} (Data Inconsistency)",
                "email": None,
                "role": "unknown",
                "registered_at": None,
                "team_count": len(self.team_members),
            }

        return {
            "id": self.id,
            "name": self.ctfd_user.name,
            "email": self.ctfd_user.email,
            "role": self.ctfd_user.type,
            "registered_at": self.ctfd_user.created,
            "team_count": len(self.team_members),
        }

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
    def get_user_teams_in_event_data(cls, user_id: int, event_id: int) -> dict[str, Any]:
        """Gets a user's team membership in a event with all related data.

        Args:
            user_id (int): The user ID.
            event_id (int): The event ID to check.

        Returns:
            dict: Contains event, team_member, team data or None values if not found.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...event.models.Event import Event
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        event = Event.query.get(event_id)
        if not event:
            return {"event": None, "team_member": None, "team": None}

        team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()
        if not team_member:
            return {"event": event, "team_member": None, "team": None}

        team = Team.query.get(team_member.team_id)
        return {"event": event, "team_member": team_member, "team": team}

    @classmethod
    def check_can_join_team_in_event(cls, user_id: int, event_id: int) -> bool:
        """Checks if a user can join a team in the event.

        Args:
            user_id (int): The user ID.
            event_id (int): The event ID to check eligibility for.

        Returns:
            bool: True if user can join, False if already in a team.
        """
        # Lazy import to prevent circular dependencies (needed)
        from ...team.models.TeamMember import TeamMember

        existing_team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()
        return existing_team_member is None

    @classmethod
    def get_user_teams_data(cls, user_id: int):
        """Gets all team members for a user across all events with optimized query.

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            list: Raw query results (Row objects), empty list if user not found
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...event.models.Event import Event
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        user = cls.query.get(user_id)
        if not user:
            return []

        team_members_query = (
            db.session.query(
                TeamMember.joined_at,
                Team.id.label("team_id"),
                Team.name.label("team_name"),
                Event.max_team_size.label("max_team_size"),
                Event.id.label("event_id"),
                Event.name.label("event_name"),
                func.count(TeamMember.id).over(partition_by=Team.id).label("team_member_count"),
            )
            .join(Team, TeamMember.team_id == Team.id)
            .join(Event, TeamMember.event_id == Event.id)
            .filter(TeamMember.user_id == user_id)
            .all()
        )
        return team_members_query

    @classmethod
    def get_user_participation_stats(cls, user_id: int) -> dict[str, Any]:
        """Gets participation stats for a user across all events.

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            dict: Stats data or None if user not found.
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...event.models.Event import Event
        from ...team.models.TeamMember import TeamMember

        user = cls.query.get(user_id)
        if not user:
            return None

        events_participated_query = db.session.query(TeamMember.event_id.distinct()).filter_by(user_id=user_id).all()
        events_participated = {event_id for (event_id,) in events_participated_query}
        total_events = Event.query.count()

        return {
            "total_team_members": TeamMember.query.filter_by(user_id=user_id).count(),
            "events_participated": len(events_participated),
            "total_events_available": total_events,
            "participation_rate": (len(events_participated) / total_events if total_events > 0 else 0),
        }

    @classmethod
    def get_total_count(cls) -> int:
        """Get the total count of all users.

        Returns:
            int: Total number of users
        """
        return cls.query.count()

    @classmethod
    def find_orphaned_users_query(cls):
        """Find users that have no team member associations (orphaned users).

        Returns:
            Query: SQLAlchemy query object for orphaned users (can be used for .all() or .delete())
        """
        # Lazy imports to prevent circular dependencies (needed)
        from ...team.models.TeamMember import TeamMember

        return cls.query.outerjoin(TeamMember, cls.id == TeamMember.user_id).filter(TeamMember.id.is_(None))

    @classmethod
    def get_all_users_with_details(cls):
        """Gets a list of all users with their core CTFd data and extended plugin data.

        Returns:
            list[User]: List of User objects with loaded relationships
        """

        return cls.query.options(db.joinedload(cls.team_members)).all()

    @classmethod
    def get_user_details_by_id(cls, user_id: int) -> "User" | None:
        """Gets detailed info for a single user by their ID.

        Args:
            user_id: The ID of the user to fetch.

        Returns:
            User: The User object with loaded relationships, or None if not found
        """

        return cls.query.options(db.joinedload(cls.team_members)).filter_by(id=user_id).first()

    @classmethod
    def cleanup_orphaned_users(cls) -> int:
        """Removes user records that have no team member associations.

        Returns:
            int: Number of users deleted
        """
        try:
            orphaned_users_query = cls.find_orphaned_users_query()
            orphaned_users = orphaned_users_query.all()
            orphaned_count = len(orphaned_users)

            if orphaned_count > 0:
                orphaned_users_query.delete(synchronize_session=False)
                db.session.commit()

            return orphaned_count
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def delete_all(cls) -> None:
        """Delete all user extensions from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
