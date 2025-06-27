from CTFd.models import db

class Tag(db.Model):
    __tablename__ = 'ng_challengetag'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ng_challenge.id'), nullable=False, index=True)
    tag = db.Column(db.String(255), nullable=False, index=True)

    challenge = db.relationship('Challenge', back_populates='tags')

    def __repr__(self):
        return f'<NgChallengeTag {self.id}>'

    @classmethod
    def create_tag(cls, **kwargs):
        try:
            tag = cls(**kwargs)
            db.session.add(tag)
            db.session.commit()
            return tag
        except Exception as e:
            db.session.rollback()
            raise e

