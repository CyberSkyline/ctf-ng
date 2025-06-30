from CTFd.models import db

class Hint(db.Model):
    __tablename__ = 'ng_challenge_hint'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ng_challenge.id'), nullable=False, index=True)
    preview = db.Column(db.String(255), nullable=False)
    hint = db.Column(db.String(255), nullable=False)
    deduction = db.Column(db.Integer, nullable=False)

    challenge = db.relationship('Challenge', back_populates='hints')

    def __repr__(self):
        return f'<NgHint {self.id}>'

    @classmethod
    def create_hint(cls, commit=True, **kwargs):
        try:
            hint = cls(**kwargs)
            db.session.add(hint)
            if commit:
                db.session.commit()
            return hint
        except Exception as e:
            db.session.rollback()
            raise e

