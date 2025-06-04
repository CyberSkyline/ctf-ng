from CTFd.models import db
from datetime import datetime

"""
connects users, teams, and worlds.
enables users to/can be in different teams across different worlds.
"""

class TeamMember(db.Model):
    __tablename__ = "ng_team_members"
    
    # composite primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey("ng_worlds.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False)
    
    # for future time limit
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # assuming a user can only be in one team per world?
    __table_args__ = (db.UniqueConstraint('user_id', 'world_id', name='uq_user_world'),)
    
    # relationships
    user = db.relationship('User', back_populates='team_memberships')
    team = db.relationship('Team', back_populates='members')
    world = db.relationship('World')
    
    def __repr__(self):
        """debugging"""
        return f'<TeamMember user={self.user_id} team={self.team_id} world={self.world_id}>'
