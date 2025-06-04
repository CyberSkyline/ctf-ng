from CTFd.models import db

"""
This is a custom team model because the native CTFd team model does not support a user to be in multiple teams.
"""


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    limit = db.Column(db.Integer, nullable=False)
    ranked = db.Column(db.Boolean, default=False)
    inviteCode = db.Column(db.String(32), nullable=False, unique=True)

    world_id = db.Column(db.Integer, db.ForeignKey('worlds.id'), nullable=False)

    world = db.relationship('World', backref='teams')
    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan')

"""

started : date
isPlaceholder : bool

"""