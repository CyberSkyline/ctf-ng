from CTFd.models import db

class ChallengeContianerInstance(db.Model):
    __tablename__ = 'challengecontainerinstance'
    id = db.Column(db.Integer, primary_key=True)
    ## Challenge Container
    challengeContainer = db.Column(db.Integer, db.ForeignKey('challengecontainer.id'))
    ## Team id
    team = db.Column(db.Integer, db.ForeignKey('teams.id'))

