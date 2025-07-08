from CTFd.models import db
from sqlalchemy import CheckConstraint

class EventRegistration(db.Model):
    __tablename__ = 'ng_event_registration'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('ng_events.id'))
    public = db.Column(db.Boolean, nullable=False, default=False)
    reg_open = db.Column(db.Boolean, nullable=False, default=False)
    reg_start_date = db.Column(db.DateTime, nullable=True)
    reg_end_date = db.Column(db.DateTime, nullable=True)

    event = db.relationship('Event', backref='registration', lazy='joined')



    __table_args__ = (
        CheckConstraint(
            "(reg_start_date IS NULL AND reg_end_date IS NULL) OR (reg_start_date IS NOT NULL AND reg_end_date IS NOT NULL)",
            name="ck_event_reg_dates_together",
        ),
        CheckConstraint(
            "reg_start_date < reg_end_date",
            name="ck_event_reg_dates_order",
        )
    )

    def __repr__(self):
        return f'<Registration Event id={self.event_id} public={self.public} reg_open={self.reg_open}>'


    @classmethod
    def create_event_registration(cls, event_id, public=False, reg_open=False, reg_start_date=None, reg_end_date=None):
        """Create and persist a new event registration to the database.

        Args:
            event_id (int): Event ID
            public (bool, optional): Whether registration is public
            reg_open (bool, optional): Whether registration is open
            reg_start_date (datetime, optional): Registration start date
            reg_end_date (datetime, optional): Registration end date

        Returns:
            EventRegistration: The created event registration instance
        """
        registration = cls(
            event_id=event_id,
            public=public,
            reg_open=reg_open,
            reg_start_date=reg_start_date,
            reg_end_date=reg_end_date,
        )

        db.session.add(registration)
        db.session.commit()
        return registration


    @classmethod
    def get_event_registration_by_event_id(cls, event_id):
        """Retrieve an event registration by its event ID.

        Args:
            event_id (int): The ID of the event to retrieve registration for.

        Returns:
            EventRegistration: The event registration instance or None if not found.
        """
        return cls.query.filter_by(event_id=event_id).first()


    @classmethod
    def get_events_available_for_registration(cls):
        """Retrieve all events that are available for registration.

        Returns:
            list: A list of EventRegistration instances that have registration open and valid date ranges.
        """
        return cls.query.filter_by(reg_open=True).filter(
            (cls.reg_start_date.is_(None) | (cls.reg_start_date <= db.func.now())) &
            (cls.reg_end_date.is_(None) | (cls.reg_end_date >= db.func.now()))
        ).all()


    def update_registration(self, public=None, reg_open=None, reg_start_date=None, reg_end_date=None):
        """Update the event registration instance with new values.

        Args:
            public (bool, optional): Whether registration is public
            reg_open (bool, optional): Whether registration is open
            reg_start_date (datetime, optional): Registration start date
            reg_end_date (datetime, optional): Registration end date

        Returns:
            EventRegistration: The updated event registration instance.
        """
        if public is not None:
            self.public = public
        if reg_open is not None:
            self.reg_open = reg_open
        if reg_start_date is not None:
            self.reg_start_date = reg_start_date
        if reg_end_date is not None:
            self.reg_end_date = reg_end_date

        db.session.commit()
        return self

    def serialize(self):
        """Serialize an event registration instance to a dictionary.

        Args:
            registration (EventRegistration): The event registration instance to serialize.

        Returns:
            dict: Serialized event registration data.
        """
        return {
            "id": self.id,
            "event_id": self.event_id,
            "public": self.public,
            "reg_open": self.reg_open,
            "reg_start_date": self.reg_start_date.isoformat() if self.reg_start_date else None,
            "reg_end_date": self.reg_end_date.isoformat() if self.reg_end_date else None,
        }