from CTFd.models import db

class Question(db.Model):
    __tablename__ = 'ng_challengequestion'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    body = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    max_attempts = db.Column(db.Integer, nullable=False)
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
