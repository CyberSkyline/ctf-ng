# /plugin/models/World.py

from CTFd.models import db


class World(db.Model):
    __tablename__ = "ng_worlds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    default_team_size = db.Column(db.Integer, default=4, nullable=False)

    teams = db.relationship("Team", backref="world", lazy=True)

    def __repr__(self):
        return f"<World {self.name}>"
