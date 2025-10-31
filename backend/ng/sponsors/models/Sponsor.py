from CTFd.models import db
from typing import Any
from ...core.utils.validator import BaseValidator


class Sponsor(db.Model):
    __tablename__ = "ng_sponsors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    logo = db.Column(db.String(256), nullable=True)

    users = db.relationship("User", back_populates="affiliation", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Sponsor id={self.id} name={self.name}>"

    def serialize(self, include_admin_fields = False) -> dict[str, Any]:
        data =  {
            "id": self.id,
            "name": self.name,
            "logo": self.logo,
        }
        return data

    @classmethod
    def create_sponsor(cls, name, logo=None, commit=True):
        sponsor = cls(name=name, logo=logo)
        db.session.add(sponsor)
        if commit:
            db.session.commit()
        return sponsor

    def update(self, commit=True, **kwargs):

        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        if commit:
            db.session.commit()
        return self
    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, sponsor_id: int):
        return cls.query.filter_by(id=sponsor_id).first()

    @classmethod
    def search_by_name(cls, name_substring: str):
        return cls.query.filter(cls.name.ilike(f"%{name_substring}%")).all()

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        validator = BaseValidator()

        validator.validate_string(data, "name", 128, required=True)

        validator.validate_url(data, "logo", required=False)

        return validator.validate()

    @classmethod
    def get_all_sponsors(cls):
        return cls.query.all()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()