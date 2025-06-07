# /plugin/models/TeamMember.py

from CTFd.models import db
from datetime import datetime
from .enums import TeamRole


class TeamMember(db.Model):
    __tablename__ = "ng_team_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    world_id = db.Column(db.Integer, db.ForeignKey("ng_worlds.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "world_id", name="uq_user_world"),
        db.Index("ix_ng_team_members_team_role", "team_id", "role"),
    )  # Users can only be in one team per world

    user = db.relationship("User", back_populates="team_memberships")
    team = db.relationship("Team", back_populates="members")
    world = db.relationship("World")

    def __repr__(self):
        return f"<TeamMember user={self.user_id} team={self.team_id} world={self.world_id}>"
