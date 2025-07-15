from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import db

from ...core.exceptions import ValidationError
from ...core.validation import BaseValidator

MAX_CHALLENGE_NAME_LENGTH = 128
MAX_CHALLENGE_DESCRIPTION_LENGTH = 4096
MAX_CHALLENGE_SUMMARY_LENGTH = 4096
MAX_CHALLENGE_ICON_LENGTH = 64


class SerializedChallenge(TypedDict):
    id: int
    name: str
    description: str = ""
    icon: str = ""
    summary: str = ""


class Challenge(db.Model):
    __tablename__ = "ng_challenges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_CHALLENGE_NAME_LENGTH), nullable=False)
    description = db.Column(db.String(MAX_CHALLENGE_DESCRIPTION_LENGTH), nullable=True)
    icon = db.Column(db.String(MAX_CHALLENGE_ICON_LENGTH), nullable=True)
    summary = db.Column(db.String(MAX_CHALLENGE_SUMMARY_LENGTH), nullable=True)

    hints = db.relationship("Hint", back_populates="challenge", cascade="all, delete-orphan")
    tags = db.relationship("ChallengeTag", back_populates="challenge", cascade="all, delete-orphan")
    questions = db.relationship("Question", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Challenge {self.id}, name={self.name}, icon={self.icon}>"

    def serialize(self, include_admin_fields=False) -> SerializedChallenge:
        """
        Serialize the challenge to a dictionary.
        :return: A dictionary representation of the challenge.
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "icon": self.icon or "",
            "summary": self.summary or "",
        }

        return SerializedChallenge(**data)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the challenge data.
        :param data: The challenge data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            MAX_CHALLENGE_NAME_LENGTH,
            required=True,
            friendly_name="Challenge Name",
        )
        validator.validate_string(
            data,
            "description",
            MAX_CHALLENGE_DESCRIPTION_LENGTH,
            required=False,
            friendly_name="Challenge Description",
        )
        validator.validate_string(
            data,
            "icon",
            MAX_CHALLENGE_ICON_LENGTH,
            required=False,
            friendly_name="Challenge Icon",
        )
        validator.validate_string(
            data,
            "summary",
            MAX_CHALLENGE_SUMMARY_LENGTH,
            required=False,
            friendly_name="Challenge Summary",
        )

        is_valid, errors, parsed_data = validator.is_valid()

        if not is_valid:
            raise ValidationError("Challenge validation failed", errors)

        return parsed_data

    @classmethod
    def create_challenge(
        cls, name: str, icon: str = "", description: str = "", summary: str = "", commit=True
    ) -> Challenge:
        try:
            validated_data = cls.validate(
                {
                    "name": name,
                    "icon": icon,
                    "description": description,
                    "summary": summary,
                }
            )
            challenge = cls(**validated_data)
            db.session.add(challenge)
            db.session.flush()
            if commit:
                db.session.commit()
            return challenge
        except Exception as e:
            db.session.rollback()
            raise e
