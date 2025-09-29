
from typing import Any
from CTFd.models import db
from sqlalchemy.orm import Mapped

from .Challenge import Challenge

from ...core.utils.validator import BaseValidator

class ChallengeYaml(db.Model):
    __tablename__ = "ng_challenge_yamls"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)
    body: Mapped[str] = db.Column(db.Text, nullable=True)

    challenge: Mapped[Challenge] = db.relationship("Challenge", back_populates="yaml")

    def __repr__(self):
        return f"<NgChallengeYaml {self.id}, challenge_id={self.challenge_id}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the challenge YAML data.
        :param data: The challenge YAML data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required=True,
            friendly_name="Challenge ID",
        )

        return validator.validate()

    @classmethod
    def create_yaml(cls, challenge_id: int, body: str, commit=True):
        try:
            validated_data = cls.validate({"challenge_id": challenge_id})

            challenge_yaml = cls(**validated_data, body=body)
            db.session.add(challenge_yaml)
            db.session.flush()

            if commit:
                db.session.commit()
            return challenge_yaml
        except Exception as e:
            db.session.rollback()
            raise e