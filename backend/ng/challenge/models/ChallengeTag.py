from typing import Any

from CTFd.models import db

from ...core.utils.validator import BaseValidator

MAX_CHALLENGE_TAG_NAME_LENGTH = 256


class ChallengeTag(db.Model):
    __tablename__ = "ng_challenge_tags"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)
    name = db.Column(db.String(MAX_CHALLENGE_TAG_NAME_LENGTH), nullable=False, index=True)

    challenge = db.relationship("Challenge", back_populates="tags")

    def __repr__(self):
        return f"<NgChallengeTag {self.id}, name={self.name}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the challenge tag data.
        :param data: The challenge tag data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            max_length=MAX_CHALLENGE_TAG_NAME_LENGTH,
            required=True,
            friendly_name="Challenge Tag Name",
        )
        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required=True,
            friendly_name="Challenge ID",
        )

        return validator.validate()

    @classmethod
    def create_tag(cls, challenge_id: int, name: str, commit=True):
        try:
            validated_data = cls.validate({"name": name, "challenge_id": challenge_id})

            tag = cls(**validated_data)
            db.session.add(tag)
            db.session.flush()

            if commit:
                db.session.commit()
            return tag
        except Exception as e:
            db.session.rollback()
            raise e
