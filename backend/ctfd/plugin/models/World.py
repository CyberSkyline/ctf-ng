# /plugin/models/World.py

from CTFd.models import db
from .. import config


class World(db.Model):
    __tablename__ = "ng_worlds"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(config.WORLD_NAME_MAX_LENGTH), nullable=False)
    description = db.Column(db.Text, nullable=True)
    default_team_size = db.Column(db.Integer, default=config.DEFAULT_TEAM_SIZE, nullable=False)

    teams = db.relationship("Team", backref="world", lazy=True)

    def __repr__(self):
        return f"<World {self.name}>"
