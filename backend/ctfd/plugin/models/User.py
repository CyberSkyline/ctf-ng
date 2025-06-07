# /plugin/models/User.py

from CTFd.models import db
from typing import Optional, Any


class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)  # links to ctfd's main users table
    team_memberships = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NgUser id={self.id}>"

    def get_team_for_world(self, world_id: int) -> Optional[Any]:
        for tm in self.team_memberships:
            if tm.world_id == world_id:
                return tm.team
        return None

    def is_in_team_for_world(self, world_id: int) -> bool:
        return any(tm.world_id == world_id for tm in self.team_memberships)
