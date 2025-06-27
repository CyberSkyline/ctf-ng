from CTFd.models import db

class Question(db.Model):
    __tablename__ = 'ng_challengequestion'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    question = db.Column(db.String(255))
    points = db.Column(db.Integer)
    answer = db.Column(db.String(255))
    max_attempts = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ng_challenge.id'), nullable=False, index=True)

    challenge = db.relationship('Challenge', back_populates='questions')

    def __repr__(self):
        return f'<NgChallengeQuestion {self.id}>'

    @classmethod
    def create_question(cls, commit=True, **kwargs):
        try:
            question = cls(**kwargs)
            db.session.add(question)
            if commit:
                db.session.commit()
            return question
        except Exception as e:
            db.session.rollback()
            raise e
