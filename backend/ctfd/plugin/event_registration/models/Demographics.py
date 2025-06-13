from CTFd.models import db


class Demographics(db.Model):
    __tablename__ = 'demographics'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('ng_events.id'))
    reg_timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Demographics user_id={self.user_id} event_id={self.event_id} reg_timestamp={self.reg_timestamp}>'

    @classmethod
    def create_demographics(cls, user_id, event_id, reg_timestamp):
        """Create and persist a new demographics entry to the database.

        Args:
            user_id (int): User ID
            event_id (int): Event ID
            reg_timestamp (datetime, optional): Registration timestamp

        Returns:
            Demographics: The created demographics instance
        """

        demographics = cls(
            user_id=user_id,
            event_id=event_id,
            reg_timestamp=reg_timestamp,
        )

        db.session.add(demographics)
        db.session.commit()
        return demographics
    