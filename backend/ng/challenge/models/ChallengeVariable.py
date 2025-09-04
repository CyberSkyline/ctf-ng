from __future__ import annotations

from CTFd.models import db

from cyber_skyline.chall_parser.compose import Variable as VariableAttr
from cyber_skyline.chall_parser.template import Template as TemplateAttr
from typing import Any
from ...core.utils.validator import BaseValidator

MAX_VARIABLE_NAME_LENGTH = 128
MAX_VARIABLE_DEFAULT_LENGTH = 1000
MAX_VARIABLE_TEMPLATE_LENGTH = 1000

class ChallengeVariable(db.Model):
    __tablename__ = "ng_challenge_variables"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    name = db.Column(db.String(MAX_VARIABLE_NAME_LENGTH), nullable=False)
    default = db.Column(db.String(MAX_VARIABLE_DEFAULT_LENGTH), nullable=False)
    template = db.Column(db.String(MAX_VARIABLE_TEMPLATE_LENGTH), nullable=False)

    challenge = db.relationship("Challenge", back_populates="variables")
    questions = db.relationship("Question", back_populates="answer_variable")

    def __repr__(self):
        return f"<NgChallengeVariable {self.id}, name={self.name}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the variable data.
        :param data: The variable data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "name",
            MAX_VARIABLE_NAME_LENGTH,
            required=True,
            friendly_name="Variable Name",
        )
        validator.validate_string(
            data,
            "default",
            MAX_VARIABLE_DEFAULT_LENGTH,
            required=True,
            friendly_name="Variable Default",
        )
        validator.validate_string(
            data,
            "template",
            MAX_VARIABLE_TEMPLATE_LENGTH,
            required=True,
            friendly_name="Variable Template",
        )
        validator.validate_model_id(
            data,
            "challenge_id",
            required=True,
            friendly_name="Challenge ID",
        )

        return validator.validate()

    @classmethod
    def create_variable(cls, challenge_id: int, name: str, default: str, template: str, commit: bool = True) -> ChallengeVariable:
        try:
            validated_data = cls.validate({"name": name, "default": default, "template": template, "challenge_id": challenge_id})
            variable = cls(**validated_data)
            db.session.add(variable)
            db.session.flush()
            if commit:
                db.session.commit()
            return variable
        except Exception as e:
            db.session.rollback()
            raise e

    def as_attr(self) -> VariableAttr:
        return VariableAttr(
            template=TemplateAttr(self.template, self.name),
            default=self.default
        )
