from CTFd.models import db

class ChallengeContainer(db.Model):
    __tablename__ = 'challengecontainer'
    id = db.Column(db.Integer, primary_key=True)
    challenge = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    ## Image name
    image = db.Column(db.String(255))
    ## Network name
    network = db.Column(db.String(255))
    ## Alias/network name
    alias = db.Column(db.String(255))
    ## Ram override
    ramOverride = db.Column(db.Integer)

    def __init__(self, challenge):
        self.challenge = challenge
