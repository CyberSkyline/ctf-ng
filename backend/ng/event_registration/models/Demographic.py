from CTFd.models import db


class Demographic(db.Model):
    __tablename__ = 'demographics'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('ng_events.id'))
    reg_timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Demographic user_id={self.user_id} event_id={self.event_id} reg_timestamp={self.reg_timestamp}>'

    @classmethod
    def create_demographic(cls, user_id, event_id, reg_timestamp):
        """Create and persist a new demographic entry to the database.

        Args:
            user_id (int): User ID
            event_id (int): Event ID
            reg_timestamp (datetime): Registration timestamp

        Returns:
            Demographics: The created demographic instance
        """

        demographic = cls(
            user_id=user_id,
            event_id=event_id,
            reg_timestamp=reg_timestamp,
        )

        db.session.add(demographic)
        db.session.commit()
        return demographic

    @classmethod
    def get_demographic_by_user_and_event(cls, user_id, event_id):
        """Retrieve demographics for a specific user and event.

        Args:
            user_id (int): User ID
            event_id (int): Event ID

        Returns:
            Demographic: The demographic entry for the user and event
        """
        return cls.query.filter_by(user_id=user_id, event_id=event_id).first()

    def serialize(self):
        """Serialize a demographic instance to a dictionary.

        Args:
            demographic (Demographic): The demographic instance to serialize

        Returns:
            dict: Serialized demographic data
        """
        return {
            "user_id": self.user_id,
            "event_id": self.event_id,
            "reg_timestamp": self.reg_timestamp.isoformat()
        }
    