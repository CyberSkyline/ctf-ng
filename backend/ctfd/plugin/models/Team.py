# /plugin/models/Team.py

from CTFd.models import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
from .. import config


class Team(db.Model):
    __tablename__ = "ng_teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.TEAM_NAME_MAX_LENGTH), nullable=False)
    limit = db.Column(db.Integer, nullable=False, default=config.DEFAULT_TEAM_SIZE)
    ranked = db.Column(db.Boolean, default=False, nullable=False)
    invite_code = db.Column(db.String(config.INVITE_CODE_MAX_LENGTH), nullable=False, unique=True)
    world_id = db.Column(db.Integer, db.ForeignKey("ng_worlds.id"), nullable=False, index=True)

    __table_args__ = (db.Index("ix_ng_teams_world_name", "world_id", "name"),)

    members = db.relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"

    # Avoids a separate query for every team's member count
    @hybrid_property
    def member_count(self):
        return len(self.members)

    @member_count.expression
    def member_count(cls):
        # Lazy import to prevent circular dependencies
        from ..models.TeamMember import TeamMember

        return select(func.count(TeamMember.id)).where(TeamMember.team_id == cls.id).scalar_subquery()

    @property
    def is_full(self):
        return self.member_count >= self.limit
