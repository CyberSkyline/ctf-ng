"""
/backend/ctfd/plugin/team/models/Team.py
Defines theTeamdatabase model and its properties, including themember_counthybrid.
"""

from CTFd.models import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
from ... import config


class Team(db.Model):
    __tablename__ = "ng_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.TEAM_NAME_MAX_LENGTH), nullable=False)
    ranked = db.Column(db.Boolean, default=False, nullable=False)
    invite_code = db.Column(db.String(config.INVITE_CODE_MAX_LENGTH), nullable=False, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    locked = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.Index("ix_ng_teams_event_name", "event_id", "name"),)

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
        # Lazy import to prevent circular dependencies (needed)
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
