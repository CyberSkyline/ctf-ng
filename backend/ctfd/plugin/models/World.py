from CTFd.models import db

class World(db.Model):
    __tablename__ = "worlds"

    world_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256))
