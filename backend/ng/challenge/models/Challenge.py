from CTFd.models import db

class Challenge(db.Model):
    __tablename__ =  'ng_challenge'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    summary = db.Column(db.String(255))

    hints = db.relationship('Hint', back_populates='challenge', cascade='all, delete-orphan')
    tags = db.relationship('Tag', back_populates='challenge', cascade='all, delete-orphan')
    questions = db.relationship('Question', back_populates='challenge', cascade='all, delete-orphan')

    @classmethod
    def create_challenge(cls, commit=True, **kwargs):
        try:
            challenge = cls(**kwargs)
            db.session.add(challenge)
            if commit:
                db.session.commit()
            return challenge
        except Exception as e:
            db.session.rollback()
            raise e

