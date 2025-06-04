from CTFd.models import db

class TeamMember(db.Model):
    __tablename__ = "team_members"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey("worlds.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'world_id', name='uq_user_world'),)

    user = db.relationship('User', back_populates='teams')
    team = db.relationship('Team', back_populates='members')

    world = db.relationship('World')