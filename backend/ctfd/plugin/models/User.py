from CTFd.models import db

"""
add our team relationships
the actual user data stays in CTFd's 'users' table.
"""

class User(db.Model):
    __tablename__ = "ng_users"

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # one user can be in multiple teams
    team_memberships = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """debugging"""
        return f'<NgUser id={self.id}>'
    
    def get_teams_in_world(self, world_id):
        """get all teams this user is in for a specific world"""
        return [tm.team for tm in self.team_memberships if tm.world_id == world_id]
    
    def is_in_team_for_world(self, world_id):
        """check if user is already in a team for this world"""
        return any(tm.world_id == world_id for tm in self.team_memberships)
