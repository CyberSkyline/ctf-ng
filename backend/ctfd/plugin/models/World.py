from CTFd.models import db

class World(db.Model):
    __tablename__ = "ng_worlds"
    id = db.Column(db.Integer, primary_key=True) # changed to 'id'

    # world name (256 -flexible)
    name = db.Column(db.String(256), nullable=False)  # added nullable=False (needs a name)
    
    # optional description of the world (flexible)
    description = db.Column(db.Text, nullable=True)
    
    # one world can have many teams
    teams = db.relationship('Team', backref='world', lazy=True)
    
    def __repr__(self):
        """debugging"""
        return f'<World {self.name}>'
