from __future__ import annotations

from typing import Any, TypedDict

from CTFd.models import db
from cyber_skyline.chall_parser.compose.challenge_info import (
    Hint as HintAttr,
)

from ... import config
from ...core.utils.validator import BaseValidator


class SerializedHint(TypedDict):
    id: int
    challenge_id: int
    preview: str
    body: str | None
    deduction: int
    is_redeemed: bool


class Hint(db.Model):
    __tablename__ = "ng_challenge_hints"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)
    preview = db.Column(db.String(config.MAX_HINT_PREVIEW_LENGTH), nullable=False)
    body = db.Column(db.String(config.MAX_HINT_BODY_LENGTH), nullable=False)
    deduction = db.Column(db.Integer, nullable=False)

    challenge = db.relationship("Challenge", back_populates="hints")

    def __repr__(self):
        return f"<NgHint {self.id}, deduction={self.deduction}, preview={self.preview}, body={self.body}>"


    def serialize(self, team=None, include_admin_fields=False) -> SerializedHint:
        """
        Serialize the hint to a dictionary.
        :param team: Optional team object to check redemption status
        :param include_admin_fields: Whether to include admin-only fields
        :return: A dictionary representation of the hint.
        """
        data = {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "preview": self.preview,
            "body": None,
            "deduction": self.deduction,
            "is_redeemed": False,
        }

        if team:
            # LAZY-IMPORT
            from ...scoring.models import HintRedemption
            redemption = HintRedemption.find_by_team_and_hint(team.id, self.id)
            if redemption:
                data["is_redeemed"] = True
                data["body"] = self.body

        if include_admin_fields: # TODO may need changes after daniels admin field
            data["body"] = self.body

        return SerializedHint(**data)

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
            config.MAX_HINT_BODY_LENGTH,
            required=True,
            friendly_name="Hint Body",
        )
        validator.validate_string(
            data,
            "preview",
            config.MAX_HINT_PREVIEW_LENGTH,
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

    @classmethod
    def find_by_id(cls, hint_id: int) -> Hint | None:
        """
        Find a hint by its ID.
        """
        return cls.query.filter_by(id=hint_id).first()

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

