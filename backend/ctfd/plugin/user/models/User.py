"""
/backend/ctfd/plugin/user/models/User.py
Defines the User extension model.
"""

from CTFd.models import db
from typing import Optional, Any


class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table
    team_members = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NgUser id={self.id}>"

    def get_team_for_event(self, event_id: int) -> Optional[Any]:
        # Lazy Import to prevent circular dependencies (needed)
        from ..team.models.TeamMember import TeamMember

        tm = TeamMember.query.filter_by(user_id=self.id, event_id=event_id).first()
        return tm.team if tm else None

    def is_in_team_for_event(self, event_id: int) -> bool:
        # Lazy Import to prevent circular dependencies (needed)
        from ..team.models.TeamMember import TeamMember

        return TeamMember.query.filter_by(user_id=self.id, event_id=event_id).first() is not None

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
