"""
Defines the Team database model and its properties
"""

from __future__ import annotations

import random
import string
from datetime import datetime
from typing import (
    Any,
    NotRequired,
    TypedDict,
    cast,
)

from CTFd.models import db
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, contains_eager, joinedload, selectinload

from ... import config
from ...core.exceptions import (
    BusinessLogicError,
    ConflictError,
    ValidationError,
)
from ...core.utils.ag_grid import apply_filter_model, apply_sort_model, paginate
from ...core.utils.validator import BaseValidator
from ...event.models.Event import Event
from ...scoring.models.Score import Score
from .enums import TeamRole
from .TeamMember import TeamMember

HEX_CHARS = string.hexdigits.lower()[:16]  # '0123456789abcdef'
SEED_LENGTH = 16  # 8 bytes for random seed


class SerializedTeam(TypedDict):
    id: int
    name: str
    event_id: int
    event_name: NotRequired[str]
    member_count: int
    ranked: bool
    seed: str | None
    invite_code: str | None  # Optional for non-admin views


class Team(db.Model):
    __tablename__ = "ng_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.TEAM_NAME_MAX_LENGTH), nullable=False)
    ranked = db.Column(db.Boolean, default=False, nullable=False)
    invite_code = db.Column(db.String(config.INVITE_CODE_MAX_LENGTH), nullable=False, unique=True)
    seed: Mapped[str] = db.Column(db.String(SEED_LENGTH), nullable=False, default=lambda: Team.generate_random_seed())
    event_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    start_timestamp = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("event_id", "name", name="uq_team_event_name"),
        db.Index("ix_ng_teams_event_name", "event_id", "name"),
    )

    members = db.relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NgTeam {self.id}, name={self.name}, invite_code={self.invite_code}, seed={self.seed}>"

    # Avoids a separate query for every team's member count
    @hybrid_property
    def member_count(self): # pyright: ignore[reportRedeclaration]
        return len(self.members)

    # Required SQLAlchemy pattern: the expression must be named *same* the property.
    @member_count.expression
    def member_count(cls):  # noqa: F811, N805  # hybrid expression: must be same name as getter (F811), arg is the class not self (N805)
        # LAZY-IMPORT: Tagging all necessary lazy imports for easy searchability & visibility.
        from .TeamMember import TeamMember

        return select(func.count(TeamMember.id)).where(TeamMember.team_id == cls.id).scalar_subquery()

    @hybrid_property
    def can_manage_team(self):
        if self.start_timestamp is not None:
            return False
        event = Event.find_by_id(self.event_id)
        if event.locked:
            return False
        if event.end_time < datetime.utcnow():
            return False
        return True



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
            "invite_code": self.invite_code,
            "start_timestamp": self.start_timestamp.isoformat() + "Z" if self.start_timestamp else None,
            "end_time": self.end_time.isoformat() + "Z" if self.end_time else None,
        }

        if self.event:
            data["event_name"] = self.event.name

        return SerializedTeam(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate team creation data. Raises ValidationError on failure."""

        validator = BaseValidator()
        if "name" in data:
            validator.validate_string(
                data,
                "name",
                config.TEAM_NAME_MAX_LENGTH,
                required=True,
                friendly_name="Team name",
                printable_only=True,
                trim_whitespace=True,
            )
        if "event_id" in data:
            validator.validate_positive_integer(data, "event_id", required=True, friendly_name="Event ID")
        if "ranked" in data:
            validator.validate_boolean(data, "ranked", friendly_name="Ranked status")
        if "invite_code" in data:
            validator.validate_string(
                data,
                "invite_code",
                config.INVITE_CODE_MAX_LENGTH,
                required=False,
                friendly_name="Invite code",
            )

        # Check if team name is unique within event
        if "name" in data and "event_id" in data:
            # TODO - Remove this temporary fix to solve the unicode db crash bug when running the db dup check
            if (data["name"].isprintable() is True and data["name"].isascii() is True):
                res = Team.name_exists_in_event_excluding_self(
                    event_id=data["event_id"],
                    name=data["name"],
                    exclude_team_id=data.get("id", 0),  # Exclude current team if updating
                )
                if res:
                    raise ValidationError(f"Team name '{data['name']}' already exists in this event.")
        if "start_timestamp" in data and "end_time" in data and data["start_timestamp"] is not None and data["end_time"] is not None:
            validator.validate_time_window(data, start_field="start_timestamp", end_field="end_time")
        else:
          if "start_timestamp" in data:
            validator.validate_datetime(data, "start_timestamp", friendly_name="Start Timestamp")
          if "end_time" in data:
            validator.validate_datetime(data, "end_time", friendly_name="End Time")

        return validator.validate()

    def self_validate(self) -> None:
        """Validate the current team instance's data.

        Raises:
            ValidationError: If validation fails
        """
        try:
            Team.validate(data=cast(dict[str, Any], self.serialize(include_admin_fields=True)))
        except ValidationError as e:
            raise ValidationError(f"Team validation failed: {e}") from e

    @classmethod
    def team_name_contains_member_name(cls, name, member_names) -> bool:
        """Check if the team name contains any member's name.

        Returns:
            bool: True if team name contains a member's name, False otherwise
        """
        name_split = [part for part in name.lower().split() if len(part) > 1]
        for member_name in member_names:
            member_name_parts = [part for part in member_name.lower().split() if len(part) > 1]
            if any(part in name_split for part in member_name_parts):
                return True

        return False

    @classmethod
    def get_unique_invite_code(cls) -> str:
        """
        Generate a unique invite code for a new team
        """
        for _attempt in range(config.INVITE_CODE_GENERATION_ATTEMPTS):
            invite_code = "".join(random.choices(HEX_CHARS, k=config.INVITE_CODE_MAX_LENGTH))
            existing = cls.query.filter_by(invite_code=invite_code).first()
            if existing is None:
                return invite_code
        # Outcomes = 16^8=4.3B, probability of collision = existing_teams / 4.3B
        # Probability = (existing_teams / 4.3B)^10 = Impossible!
        raise RuntimeError(f"Failed to generate unique invite code after {config.INVITE_CODE_GENERATION_ATTEMPTS} attempts")

    @classmethod
    def generate_random_seed(cls) -> str:
        """Generate a random 8-byte seed for team creation."""
        return "".join(random.choices(HEX_CHARS, k=SEED_LENGTH))

    @classmethod
    def create_team(
        cls,
        name: str,
        event_id: int,
        invite_code: str | None = None,
        seed: str | None = None,
        ranked: bool = True,
        commit: bool = True,
    ):
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
        if seed is None:
            seed = cls.generate_random_seed()
        validated_data = cls.validate(
            data={"name": name, "event_id": event_id, "invite_code": invite_code, "seed": seed, "ranked": ranked}
        )
        team = cls(**validated_data)
        db.session.add(team)
        db.session.flush()

        # LAZY-IMPORT
        from ...scoring.models.Score import Score

        Score.create_score(team_id=team.id, commit=False, team=team)

        if commit:
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                if "uq_team_event_name" in str(e):
                    raise ConflictError(f"Team name '{name}' already exists for event ID {event_id}.") from e
                raise
        return team

    def disband_team(self, commit=True):
        """Delete this team and all its members from the database."""

        score = Score.find_by_team(self.id)
        if score:
            score.delete(commit=False)
        db.session.delete(self)
        if commit:
            db.session.commit()

    def set_end_time(self, end_time: datetime | None = None, commit=True):
        """Set the team's end time."""
        end_time = end_time.replace(tzinfo=None) if end_time is not None else None
        if end_time is not None and self.event.end_time and end_time > self.event.end_time:
            self.end_time = self.event.end_time
        else:
            self.end_time = end_time
        if commit:
            db.session.commit()

    def set_start_timestamp(self, timestamp: datetime | None = None, commit=True):
        """Set the team's start timestamp."""
        self.start_timestamp = timestamp
        if commit:
            db.session.commit()

    def update_invite_code(self, new_code: str | None = None, commit=True):
        """Update team invite code and persist to database."""
        if new_code is None:
            new_code = Team.get_unique_invite_code()

        self.invite_code = new_code

        if commit:
            db.session.commit()

    def update_team(self, **kwargs):
        """Update team attributes and persist to database."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        # LAZY-IMPORT
        from ...scoring.models.Score import Score

        self.self_validate()

        if "name" in kwargs:
            Score.query.filter_by(team_id=self.id).update({"team_name": kwargs["name"]})

        db.session.commit()
        return self

    def add_member(self, user_id: int, role: TeamRole = TeamRole.MEMBER, commit=True):
        """Add a member to the team.

        Args:
            user_id (int): The user ID to add
            role (TeamRole): The role of the member in the team
            commit (bool): Whether to commit the transaction

        Returns:
            TeamMember: The created team member instance
        """
        # LAZY-IMPORT
        from ...event.models.Event import Event
        from .TeamMember import TeamMember

        event = Event.find_by_id(self.event_id)

        if self.member_count >= event.max_team_size:
            raise ConflictError(
                f"Cannot add member: team '{self.name}' is full ({self.member_count}/{event.max_team_size})"
            )

        if self.end_time is not None and datetime.utcnow() > self.end_time:
            raise BusinessLogicError("Cannot join a team that has already finished the event")

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
    def find_paginated(cls, sort_model, filter_model, start_row, end_row) -> tuple[list[Team], int]:
        """Fetch a page of teams for the admin grid's server-side row model.

        Returns (teams, total_count) with the ag-grid sort/filter model applied.
        """
        # Also the allowlist for filter/sort.
        column_map = {
            "id": cls.id,
            "name": cls.name,
            "event_name": Event.name,
            "member_count": cls.member_count,
            "start_timestamp": cls.start_timestamp,
            "end_time": cls.end_time,
            "ranked": cls.ranked,
            "invite_code": cls.invite_code,
        }
        query = (cls.query
            .join(Event, cls.event_id == Event.id)
            .options(contains_eager(cls.event), selectinload(cls.members))
        )
        query = apply_filter_model(query, filter_model, column_map)
        query = apply_sort_model(query, sort_model, column_map, cls.id)
        return paginate(query, start_row, end_row)

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
        # LAZY-IMPORT
        from .TeamMember import TeamMember

        return cls.query.join(TeamMember).filter(TeamMember.user_id == user_id, cls.event_id == event_id).first()

    @classmethod
    def find_all_by_event(cls, event_id: int) -> list[Team]:
        """Find all teams in a specific event.

        Args:
            event_id (int): The event ID to search within

        Returns:
            list[Team]: List of teams in the event
        """
        return cls.query.filter_by(event_id=event_id).options(joinedload(cls.event)).all()

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
        # LAZY-IMPORT
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
        commit: bool = True,
    ) -> Team:
        """
        Creates a team, assigns the creator as captain, and creates a demographic
        record in a single, atomic transaction.
        """
        # LAZY-IMPORT
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

    def count_correct_attempts_in_event(self, event_id: int) -> int:
        """
        Counts the number of correctly answered questions by this team in a given event
        """
        # LAZY-IMPORT
        from ...scoring.models.Attempt import Attempt

        return Attempt.query.filter_by(
            team_id=self.id,
            event_id=event_id,
            is_correct=True,
        ).count()

    def has_solved_question(self, question_id: int) -> bool:
        """
        Checks if the team has already correctly answered a specific question
        """
        # LAZY-IMPORT
        from ...scoring.models.Attempt import Attempt

        return (
            Attempt.query.filter_by(
                team_id=self.id,
                question_id=question_id,
                is_correct=True,
            ).first()
            is not None
        )

    def has_redeemed_hint(self, hint_id: int) -> bool:
        """
        Checks if the team has already redeemed a specific hint
        """
        # LAZY-IMPORT
        from ...scoring.models.HintRedemption import HintRedemption

        return HintRedemption.query.filter_by(team_id=self.id, hint_id=hint_id).first() is not None

    def get_redeemed_hints_for_challenge(self, challenge_id: int) -> list[int]:
        """
        Gets a list of hint IDs this team has redeemed for a specific challenge
        """
        # LAZY-IMPORT
        from ...challenge.models.Hint import Hint
        from ...scoring.models.HintRedemption import HintRedemption

        redemptions = (
            HintRedemption.query.join(Hint)
            .filter(
                HintRedemption.team_id == self.id,
                Hint.challenge_id == challenge_id,
            )
            .all()
        )
        return [r.hint_id for r in redemptions]

    def remove_member_and_regenerate_code(self, user_id: int, commit=True) -> None:
        """Remove a team member and regenerate invite code in single transaction."""
        # LAZY-IMPORT
        from .TeamMember import TeamMember

        try:
            member = TeamMember.query.filter_by(team_id=self.id, user_id=user_id).first()
            if not member:
                raise ValidationError(f"User {user_id} is not a member of team {self.id}.")
            if member:
                member.remove_team_member(commit=False)
                self.update_invite_code(commit=False)
                if commit:
                    db.session.commit()
                return
        except Exception:
            db.session.rollback()
            raise

    def remove_captain_and_promote(self, new_captain_user_id: int) -> bool:
        """Remove captain and promote new one in single transaction."""
        # LAZY-IMPORT
        from .enums import TeamRole
        from .TeamMember import TeamMember

        try:
            captain = TeamMember.query.filter_by(team_id=self.id, role=TeamRole.CAPTAIN).first()
            if captain:
                captain.update_role(TeamRole.MEMBER, commit=False)

            new_captain = TeamMember.query.filter_by(team_id=self.id, user_id=new_captain_user_id).first()
            if new_captain:
                new_captain.update_role(TeamRole.CAPTAIN, commit=False)
            else:
                raise ValidationError(f"User {new_captain_user_id} is not a member of team {self.id}.")

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
