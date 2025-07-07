"""
/backend/ng/user/models/User.py
Defines the User extension model.
"""

from CTFd.models import db
from CTFd.models import Users as CTFdUsers
from sqlalchemy import func
from typing import Any
from sqlalchemy.ext.associationproxy import association_proxy


class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table
    team_members = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    user_roles = db.relationship("UserRole",back_populates="user",cascade="all, delete-orphan",)

    roles = association_proxy("user_roles","role",creator=lambda role: UserRole(role=role))

    def __repr__(self):
        return f"<NgUser id={self.id}>"

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
        from ...team.models.TeamMember import TeamMember

        existing_team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()
        return existing_team_member is None

    @classmethod
    def get_user_teams_data(cls, user_id: int) -> list[dict]:
        """Gets all team members for a user across all events with optimized query.

        Args:
            user_id (int): The user ID to get teams for.

        Returns:
            list[dict]: List of team data with event info, empty list if user not found.
        """
        from ...event.models.Event import Event
        from ...team.models.Team import Team
        from ...team.models.TeamMember import TeamMember

        user = cls.query.get(user_id)
        if not user:
            return []

        # Single query with member count
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

        return [
            {
                "team_id": team_member.team_id,
                "team_name": team_member.team_name,
                "event_id": team_member.event_id,
                "event_name": team_member.event_name,
                "joined_at": team_member.joined_at.isoformat() if team_member.joined_at else None,
                "max_team_size": team_member.max_team_size,
                "team_member_count": team_member.team_member_count,
            }
            for team_member in team_members_query
        ]

    @classmethod
    def get_user_participation_stats(cls, user_id: int) -> dict[str, Any]:
        """Gets participation stats for a user across all events.

        Args:
            user_id (int): The user ID to get stats for.

        Returns:
            dict: Stats data or None if user not found.
        """
        from ...event.models.Event import Event
        from ...team.models.TeamMember import TeamMember

        user = cls.query.get(user_id)
        if not user:
            return None

        # Direct query for distinct event IDs, avoids loading objects
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
        from ...team.models.TeamMember import TeamMember

        return cls.query.outerjoin(TeamMember, cls.id == TeamMember.user_id).filter(TeamMember.id.is_(None))

    @classmethod
    def get_all_users_with_details(cls) -> list[dict[str, Any]]:
        """
        Gets a list of all users with their core CTFd data and extended
        plugin data, like team count.

        Returns:
            list[dict]: A list of dictionaries, each representing a user.
        """
        from ...team.models.TeamMember import TeamMember

        # Query to join plugin users, CTFd users, and count team memberships
        users_query = (
            db.session.query(
                CTFdUsers.id,
                CTFdUsers.name,
                CTFdUsers.email,
                CTFdUsers.type.label("role"),
                CTFdUsers.created.label("registered_at"),
                func.count(TeamMember.id).label("team_count"),
            )
            .join(cls, CTFdUsers.id == cls.id)
            .outerjoin(TeamMember, cls.id == TeamMember.user_id)
            .group_by(
                CTFdUsers.id,
                CTFdUsers.name,
                CTFdUsers.email,
                CTFdUsers.type,
                CTFdUsers.created,
            )
            .order_by(CTFdUsers.id)
            .all()
        )

        users_list = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "registered_at": user.registered_at.isoformat() if user.registered_at else None,
                "team_count": user.team_count,
            }
            for user in users_query
        ]

        return users_list


    def serialize(self) -> dict[str, Any]:
        """Serialize the User instance to a dictionary.

        Returns:
            dict: Serialized user data
        """
        return {
            "id": self.id,
            "roles": [role.serialize() for role in self.roles],
            "team_members": [tm.serialize() for tm in self.team_members],
        }

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