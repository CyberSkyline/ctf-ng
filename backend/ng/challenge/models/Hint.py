from typing import Any

from CTFd.models import db
from cyber_skyline.chall_parser.compose.challenge_info import Hint as HintAttr

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

    def serialize(self, include_admin_fields=False) -> dict[str, Any]:
        """
        Serialize the hint to a dictionary.
        :return: A dictionary representation of the hint.
        """
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "preview": self.preview,
            "body": self.body,
            "deduction": self.deduction,
        }

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
        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required=True,
            friendly_name="Challenge ID",
        )

        return validator.validate()

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

    def as_attr(self) -> HintAttr:
        """
        Convert the Hint model to a HintAttr object.
        :return: A HintAttr object representing the hint.
        """
        return HintAttr(
            body=self.body,  # type: ignore
            preview=self.preview,  # type: ignore
            deduction=self.deduction,  # type: ignore
        )
