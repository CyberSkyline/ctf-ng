from CTFd.models import db
from sqlalchemy.orm import validates

class EventRegistration(db.Model):
    __tablename__ = 'ng_event_registration'
    reg_id = db.Column(db.Integer, primary_key=True)
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
    )

    def __repr__(self):
        return f'<Registration Event id={self.world_id} public={self.public} reg_open={self.reg_open}>'


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