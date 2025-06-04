from CTFd.models import db

"""
This is a custom team model because the native CTFd team model does not support a user to be in multiple teams.
Our model allows users to be in different teams across different worlds.
"""

class Team(db.Model):
    __tablename__ = 'ng_teams'

    # changed to 'id'
    id = db.Column(db.Integer, primary_key=True)

    # team name
    name = db.Column(db.String(128), nullable=False)  # Added length limit

    # Max allowed on team
    limit = db.Column(db.Integer, nullable=False, default=4) # (flexible)

    # if team appears on public scoreboards (yes or no)
    ranked = db.Column(db.Boolean, default=False, nullable=False)

    # invite code
    invite_code = db.Column(db.String(32), nullable=False, unique=True)  # changed to snake_case

    # world this team exists in
    world_id = db.Column(db.Integer, db.ForeignKey('ng_worlds.id'), nullable=False)

    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan')

    def __repr__(self):
        """for debugging"""
        return f'<Team {self.name} in World {self.world_id}>'

    @property
    def member_count(self):
        """number of members"""
        return len(self.members)

    @property
    def is_full(self):
        """if team is at capacity"""
        return self.member_count >= self.limit
