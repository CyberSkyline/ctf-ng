from typing import Any

from CTFd.models import db

from ...core.exceptions import ValidationError
from ...core.validation import BaseValidator

MAX_HINT_PREVIEW_LENGTH = 256
MAX_HINT_BODY_LENGTH = 1024


class Hint(db.Model):
    __tablename__ = "ng_challenge_hints"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)
    preview = db.Column(db.String(MAX_HINT_PREVIEW_LENGTH), nullable=False)
    body = db.Column(db.String(MAX_HINT_BODY_LENGTH), nullable=False)
    deduction = db.Column(db.Integer, nullable=False)

    challenge = db.relationship("Challenge", back_populates="hints")

    def __repr__(self):
        return f"<NgHint {self.id}, deduction={self.deduction}, preview={self.preview}, body={self.body}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the hint data.
        :param data: The hint data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "body",
            MAX_HINT_BODY_LENGTH,
            required=True,
            friendly_name="Hint Body",
        )
        validator.validate_string(
            data,
            "preview",
            MAX_HINT_PREVIEW_LENGTH,
            required=False,
            friendly_name="Hint Preview",
        )
        validator.validate_positive_integer(
            data,
            "deduction",
            required=True,
            friendly_name="Hint Deduction",
        )
        validator.validate_positive_integer(
            data,
            "challenge_id",
            required=True,
            friendly_name="Challenge ID",
        )

        is_valid, errors, parsed_data = validator.is_valid()

        if not is_valid:
            raise ValidationError("Hint validation failed", errors)

        return parsed_data

    @classmethod
    def create_hint(cls, challenge_id: int, body: str, preview: str = "", deduction: int = 0, commit=True):
        try:
            validated_data = cls.validate(
                {"preview": preview, "body": body, "deduction": deduction, "challenge_id": challenge_id}
            )
            hint = cls(**validated_data)
            db.session.add(hint)
            db.session.flush()
            if commit:
                db.session.commit()
            return hint
        except Exception as e:
            db.session.rollback()
            raise e
