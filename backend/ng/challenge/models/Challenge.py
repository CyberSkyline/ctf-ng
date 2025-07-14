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


class QuestionYaml(TypedDict):
    name: str
    body: str
    points: int
    answer: str
    max_attempts: int


class HintYaml(TypedDict):
    body: str
    preview: str = ""
    deduction: int = 0


class ServiceYaml(TypedDict):
    image: str
    hostname: str
    networks: list[str]


class NetworkYaml(TypedDict):
    internal: bool


class ChallengeYaml(TypedDict):
    name: str
    icon: str = ""
    description: str = ""
    summary: str = ""
    questions: list[QuestionYaml]
    hints: list[HintYaml]
    tags: list[str]
    services: dict[str, ServiceYaml]
    networks: dict[str, NetworkYaml]


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
            if commit:
                db.session.commit()
            return challenge
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def create_from_yaml(cls, yaml: ChallengeYaml, commit=True) -> Challenge:
        """
        Create a challenge from a YAML file.
        :param commit: Whether to commit the session after adding the challenge.
        :param kwargs: Keyword arguments for challenge attributes.
        :return: The created challenge instance.
        """
        from .ChallengeTag import ChallengeTag
        from .ContainerBlueprint import ContainerBlueprint
        from .Hint import Hint

        try:
            challenge = cls.create_challenge(
                name=yaml["name"],
                icon=yaml["icon"],
                description=yaml["description"],
                summary=yaml["summary"],
                commit=False,
            )

            for hint in yaml["hints"]:
                Hint.create_hint(challenge_id=challenge.id, **hint, commit=False)

            for tag in yaml["tags"]:
                ChallengeTag.create_tag(challenge_id=challenge.id, name=tag, commit=False)

            for blueprint in yaml["services"].items():
                ContainerBlueprint.create_container_blueprint(challenge_id=challenge.id, **blueprint[1], commit=False)

            if commit:
                db.session.commit()
            return challenge
        except Exception as e:
            db.session.rollback()
            raise e
