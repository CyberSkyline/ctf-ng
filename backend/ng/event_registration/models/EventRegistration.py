from CTFd.models import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class EventRegistration(db.Model):
    __tablename__ = 'ng_event_registration'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('ng_events.id'))
    public = db.Column(db.Boolean, nullable=False, default=False)
    reg_open = db.Column(db.Boolean, nullable=False, default=False)
    reg_start_date = db.Column(db.DateTime, nullable=True)
    reg_end_date = db.Column(db.DateTime, nullable=True)



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
    def event_joinable(cls, event_id: int):
        """Check if an event is joinable based on its registration status.

        Args:
            event_id (int): The ID of the event to check.

        Returns:
            tuple: A tuple containing a boolean indicating if the event is joinable and a string message.
        """
        registration = cls.query.filter_by(event_id=event_id).first()
        if not registration:
            return False, "Event registration not found"

        if not registration.reg_open:
            return False, "Event registration is closed"

        if registration.reg_start_date and registration.reg_start_date > datetime.now():
            return False, "Event registration has not started yet"

        if registration.reg_end_date and registration.reg_end_date < datetime.now():
            return False, "Event registration has ended"

        return True, "Event is joinable"

