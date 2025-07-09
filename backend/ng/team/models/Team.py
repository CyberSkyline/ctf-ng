"""
Defines the Team database model and its properties
"""

from __future__ import annotations
from typing import Any, TypedDict, cast
import string
import random

from CTFd.models import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func

from ... import config
from ...core.validation import BaseValidator
from ...core.exceptions import ConflictError, ValidationError
from .enums import TeamRole

HEX_CHARS = string.hexdigits.lower()[:16]  # '0123456789abcdef'

class SerializedTeam(TypedDict):
    id: int
    name: str
    event_id: int
    member_count: int
    ranked: bool
    locked: bool
    invite_code: str | None  # Optional for non-admin views

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
        from .TeamMember import TeamMember

        return select(func.count(TeamMember.id)).where(TeamMember.team_id == cls.id).scalar_subquery()

    def serialize(self, include_admin_fields: bool = False) -> SerializedTeam:
        """Serialize team for API response.

        Args:
            include_admin_fields: Whether to include admin-only fields

        Returns:
            dict: Serialized team data
        """
        data = {
            "id": self.id,
            "name": self.name,
            "event_id": self.event_id,
            "member_count": self.member_count,
            "ranked": self.ranked,
            "locked": self.locked,
        }

        if include_admin_fields:
            data["invite_code"] = self.invite_code

        return SerializedTeam(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate team creation data. Raises ValidationError on failure."""

        validator = BaseValidator()
        validator.validate_string(
            data,
            "name",
            config.TEAM_NAME_MAX_LENGTH,
            required=True,
            friendly_name="Team name",
        )
        validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")
        validator.validate_boolean(data, "ranked", friendly_name="Ranked status")
        validator.validate_string(
            data,
            "invite_code",
            config.INVITE_CODE_MAX_LENGTH,
            required=False,
            friendly_name="Invite code",
        )

        # TODO - Check if invite code is unique
        # TODO - Check if team name is unique within event

        is_valid, errors, parsed_data = validator.is_valid()

        if not is_valid:
            raise ValidationError("Validation failed.", errors=errors)
        return parsed_data
    
    def self_validate(self) -> None:
        """Validate the current team instance's data.

        Raises:
            ValidationError: If validation fails
        """
        try:
            Team.validate(data=cast(dict[str, Any], self.serialize(include_admin_fields=True)))
        except ValidationError as e:
            raise ValidationError(f"Team validation failed: {e.errors}") from e
    
    @classmethod
    def get_unique_invite_code(cls) -> str:
        """Generate a unique invite code for a new team."""
        # TODO - Raise an exception if this loops too many times
        while True:
            invite_code = ''.join(random.choices(HEX_CHARS, k=config.INVITE_CODE_MAX_LENGTH))
            existing = cls.query.filter_by(invite_code=invite_code).first()
            if existing is None:
                return invite_code


    @classmethod
    def create_team(cls, name : str, event_id : int, invite_code : str | None = None, ranked : bool = True, commit : bool = True):
        """Create and persist a new team to the database.

        Args:
            name (str): Team name
            event_id (int): Associated event ID
            invite_code (str): Team invite code
            ranked (bool, optional): Whether team is ranked
            commit (bool, optional)

        Returns:
            Team: The created team instance
        """
        if invite_code is None:
            invite_code = cls.get_unique_invite_code()

        validated_data = cls.validate(data = { "name": name, "event_id": event_id, "invite_code": invite_code, "ranked": ranked })

        team = cls(**validated_data)

        db.session.add(team)
        db.session.flush()
        if commit:
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                if "uq_team_event_name" in str(IntegrityError):
                    raise ConflictError(f"Team name '{name}' already exists for event ID {event_id}.")
                raise

        return team

    def disband_team(self, commit=True):
        """Delete this team and all its members from the database."""

        # TODO - Throw an error if the team still has remaining members

        db.session.delete(self)
        if commit:
            db.session.commit()

    def update_invite_code(self, new_code: str | None = None, commit=True):
        """Update team invite code and persist to database."""
        if new_code is None:
            new_code = Team.get_unique_invite_code()

        self.invite_code = new_code

        self.self_validate()

        if commit:
            db.session.commit()

    def update_name(self, new_name, commit=True):
        """Update team name and persist to database."""
        self.name = new_name

        if commit:
            db.session.commit()

    def add_member(self, user_id: int, role: TeamRole = TeamRole.MEMBER, commit=True):
        """Add a member to the team.

        Args:
            user_id (int): The user ID to add
            role (TeamRole): The role of the member in the team
            commit (bool): Whether to commit the transaction

        Returns:
            TeamMember: The created team member instance
        """
        from .TeamMember import TeamMember
        from ...event.models.Event import Event

        event = Event.find_by_id(self.event_id)

        if self.member_count >= event.max_team_size:
            raise ConflictError(f"Cannot add member: team '{self.name}' is full ({self.member_count}/{event.max_team_size})")

        member = TeamMember.create_team_member(
            user_id=user_id,
            team_id=self.id,
            event_id=self.event_id,
            role=role,
        )

        db.session.add(member)
        if commit:
            db.session.commit()
        return member

    @classmethod
    def get_all_teams(cls) -> list[Team]:
        """Gets all teams for admin purposes.

        Returns:
            list[Team]: List of all team objects
        """
        return cls.query.order_by(cls.id).all()

    @classmethod
    def find_by_id(cls, team_id: int) -> Team | None:
        """Find a team by ID.

        Args:
            team_id (int): The team ID to find

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.get(team_id)

    @classmethod
    def find_by_invite_code(cls, invite_code: str) -> Team | None:
        """Find a team by invite code.

        Args:
            invite_code (str): The invite code to find

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.filter_by(invite_code=invite_code).first()

    @classmethod
    def find_by_name_and_event(cls, name: str, event_id: int) -> Team | None:
        """Find a team by name within a specific event.

        Args:
            name (str): The team name to find
            event_id (int): The event ID to search within

        Returns:
            Team or None: The team instance if found, None otherwise
        """
        return cls.query.filter_by(name=name, event_id=event_id).first()

    @classmethod
    def find_by_user_and_event(cls, user_id: int, event_id: int) -> Team | None:
        from .TeamMember import TeamMember

        return cls.query.join(TeamMember).filter(
            TeamMember.user_id == user_id,
            cls.event_id == event_id
        ).first()

    @classmethod
    def find_all_by_event(cls, event_id: int) -> list[Team]:
        """Find all teams in a specific event.

        Args:
            event_id (int): The event ID to search within

        Returns:
            list[Team]: List of teams in the event
        """
        return cls.query.filter_by(event_id=event_id).all()

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

    def get_full_team_details(self):
        """Gets all details for a team, including event info and member list.

        Returns:
            dict: Team object with related data
        """
        from ...event.models.Event import Event
        from .TeamMember import TeamMember

        event = Event.find_by_id(self.event_id)
        team_members = TeamMember.find_all_by_team(self.id)

        return {"team": self, "event": event, "team_members": team_members}

    @classmethod
    def create_team_with_captain(
        cls,
        name: str,
        event_id: int,
        captain_id: int,
        invite_code: str | None = None,
        ranked: bool = True,
        commit: bool = True
    ) -> Team:
        """
        Creates a team, assigns the creator as captain, and creates a demographic
        record in a single, atomic transaction.
        """
        
        from .TeamMember import TeamMember
        from .enums import TeamRole

        try:
            team = cls.create_team(
                name=name,
                event_id=event_id,
                ranked=ranked,
                invite_code=invite_code,
                commit=commit,
            )

            TeamMember.create_team_member(
                user_id=captain_id,
                team_id=team.id,
                event_id=event_id,
                role=TeamRole.CAPTAIN,
                commit=commit,
            )

            if commit:
                db.session.commit()
            return team

        except Exception as e:
            db.session.rollback()
            raise e

    def remove_member_and_regenerate_code(self, user_id: int, commit = True) -> None:
        """Remove a team member and regenerate invite code in single transaction."""

        from .TeamMember import TeamMember

        try:
            member = TeamMember.find_by_user_and_event(user_id=user_id, event_id=self.event_id)
            if member:
                member.remove_team_member(commit=False)
                self.update_invite_code(commit=False)
                if commit:
                    db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def remove_captain_and_promote(self, captain_id: int, new_captain_user_id: int) -> bool:
        """Remove captain and promote new one in single transaction."""

        from .TeamMember import TeamMember
        from .enums import TeamRole

        try:
            captain = TeamMember.query.get(captain_id)
            if captain:
                captain.remove_team_member(commit=False)

            new_captain = TeamMember.query.filter_by(team_id=self.id, user_id=new_captain_user_id).first()
            if new_captain:
                new_captain.update_role(TeamRole.CAPTAIN, commit=False)

            self.update_invite_code(commit=False)

            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def delete_all(cls) -> None:
        """Delete all teams from the database."""
        try:
            cls.query.delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
