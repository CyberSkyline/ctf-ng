"""
/backend/ctfd/plugin/team/models/TeamMember.py
Defines the TeamMember model, link between users, teams, and events.
"""

from CTFd.models import db
from datetime import datetime
from .enums import TeamRole


class TeamMember(db.Model):
    __tablename__ = "ng_team_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("ng_events.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
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

    @classmethod
    def create_team_member(cls, user_id, team_id, event_id, role=TeamRole.MEMBER, joined_at=None):
        """Create and persist a new team member to the database.

        Args:
            user_id (int): User ID
            team_id (int): Team ID
            event_id (int): Event ID
            role (TeamRole, optional): Member role
            joined_at (datetime, optional): Join timestamp

        Returns:
            TeamMember: The created team member instance
        """
        if joined_at is None:
            joined_at = datetime.utcnow()

        team_member = cls(
            user_id=user_id,
            team_id=team_id,
            event_id=event_id,
            joined_at=joined_at,
            role=role,
        )

        db.session.add(team_member)
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
