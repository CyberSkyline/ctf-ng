"""
/backend/ctfd/plugin/team/models/Team.py
Defines theTeamdatabase model and its properties, including themember_counthybrid.
"""

from CTFd.models import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import Any
from ... import config


class Team(db.Model):
    __tablename__ = "ng_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.TEAM_NAME_MAX_LENGTH), nullable=False)
    ranked = db.Column(db.Boolean, default=False, nullable=False)
    invite_code = db.Column(db.String(config.INVITE_CODE_MAX_LENGTH), nullable=False, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    locked = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("event_id", "name", name="uq_team_event_name"),
        db.Index("ix_ng_teams_event_name", "event_id", "name"),
    )

    members = db.relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"

    # Avoids a separate query for every team's member count
    @hybrid_property
    def member_count(self):
        return len(self.members)

    # Required SQLAlchemy pattern: the expression must be named after the property.
    @member_count.expression
    def member_count(cls):
        # Lazy imports to prevent circular dependencies (needed)
        from .TeamMember import TeamMember

        return select(func.count(TeamMember.id)).where(TeamMember.team_id == cls.id).scalar_subquery()

    @classmethod
    def create_team(cls, name, event_id, invite_code, ranked=False, flush_only=False):
        """Create and persist a new team to the database.

        Args:
            name (str): Team name
            event_id (int): Associated event ID
            invite_code (str): Team invite code
            ranked (bool, optional): Whether team is ranked
            flush_only (bool, optional): If True, only flush, don't commit

        Returns:
            Team: The created team instance
        """
        team = cls(
            name=name,
            event_id=event_id,
            ranked=ranked,
            invite_code=invite_code,
        )

        db.session.add(team)
        if flush_only:
            db.session.flush()
        else:
            db.session.commit()
        return team

    def disband_team(self):
        """Delete this team and all its members from the database."""
        db.session.delete(self)
        db.session.commit()

    def update_invite_code(self, new_code=None, commit=True):
        """Update team invite code and persist to database."""
        if new_code is None:
            from ..controllers._generate_invite_code import _generate_invite_code

            new_code = _generate_invite_code()
        self.invite_code = new_code
        if commit:
            db.session.commit()

    def update_name(self, new_name, commit=True):
        """Update team name and persist to database."""
        self.name = new_name
        if commit:
            db.session.commit()

    @classmethod
    def find_by_id(cls, team_id: int):
        """Find a team by ID.

        Args:
            team_id (int): The team ID to find

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.get(team_id)

    @classmethod
    def find_by_invite_code(cls, invite_code: str):
        """Find a team by invite code.

        Args:
            invite_code (str): The invite code to find

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.filter_by(invite_code=invite_code).first()

    @classmethod
    def find_by_name_and_event(cls, name: str, event_id: int):
        """Find a team by name within a specific event.

        Args:
            name (str): The team name to find
            event_id (int): The event ID to search within

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.filter_by(name=name, event_id=event_id).first()

    @classmethod
    def find_all_by_event(cls, event_id: int) -> list["Team"]:
        """Find all teams in a specific event.

        Args:
            event_id (int): The event ID to search within

        Returns:
            list[Team]: List of teams in the event
        """
        return cls.query.filter_by(event_id=event_id).all()

    @classmethod
    def name_exists_in_event_excluding_self(cls, event_id: int, name: str, exclude_team_id: int) -> bool:
        """Check if a team name already exists in an event, excluding a specific team.

        Args:
            event_id (int): The event ID to check within
            name (str): The team name to check
            exclude_team_id (int): Team ID to exclude from the check

        Returns:
            bool: True if name exists (conflict), False if available
        """
        existing = cls.query.filter(
            cls.event_id == event_id,
            cls.name == name,
            cls.id != exclude_team_id,
        ).first()
        return existing is not None

    @classmethod
    def is_invite_code_unique(cls, invite_code: str) -> bool:
        """Check if an invite code is unique across all teams.

        Args:
            invite_code (str): The invite code to check

        Returns:
            bool: True if unique, False if already exists
        """
        existing = cls.query.filter_by(invite_code=invite_code).first()
        return existing is None

    @classmethod
    def get_total_count(cls) -> int:
        """Get the total count of all teams.

        Returns:
            int: Total number of teams
        """
        return cls.query.count()

    @classmethod
    def count_by_event(cls, event_id: int) -> int:
        """Get the count of teams in a specific event.

        Args:
            event_id (int): The event ID to count teams for

        Returns:
            int: Number of teams in the event
        """
        return cls.query.filter_by(event_id=event_id).count()

    @classmethod
    def delete_by_event(cls, event_id: int) -> int:
        """Delete all teams in a specific event.

        Args:
            event_id (int): The event ID to delete teams from

        Returns:
            int: Number of teams deleted
        """
        count = cls.query.filter_by(event_id=event_id).delete()
        db.session.commit()
        return count

    @classmethod
    def find_empty_teams(cls) -> list[dict[str, Any]]:
        """Find all teams that have no members.

        Returns:
            list[dict]: List of empty team data with id, name, and event_id
        """

        empty_teams_query = db.session.query(cls.id, cls.name, cls.event_id).filter(cls.member_count == 0).all()

        return [
            {"id": team_id, "name": team_name, "event_id": event_id}
            for team_id, team_name, event_id in empty_teams_query
        ]

    @classmethod
    def create_team_with_captain(
        cls,
        name: str,
        event_id: int,
        creator_id: int,
        invite_code: str,
        ranked: bool = False,
    ) -> tuple[bool, dict]:
        """
        Creates a team and assigns creator as captain in a single transaction.

        Returns:
            tuple: (success: bool, result: dict)
        """
        try:
            team = cls.create_team(
                name=name,
                event_id=event_id,
                ranked=ranked,
                invite_code=invite_code,
                flush_only=True,
            )

            from ...user.models.User import User

            ng_user = User.find_by_id(creator_id)
            if not ng_user:
                ng_user = User.create_user(creator_id, commit=False)

            from .TeamMember import TeamMember
            from .enums import TeamRole
            from datetime import datetime

            TeamMember.create_team_member(
                user_id=creator_id,
                team_id=team.id,
                event_id=event_id,
                role=TeamRole.CAPTAIN,
                joined_at=datetime.utcnow(),
                commit=False,
            )

            db.session.commit()

            return True, {"team": team, "message": "Team created successfully"}

        except IntegrityError as e:
            db.session.rollback()
            if "uq_team_event_name" in str(e) or "UNIQUE constraint failed" in str(e):
                return False, {"error": f"Team '{name}' already exists in this event"}
            else:
                raise e

        except Exception as e:
            db.session.rollback()
            raise e
