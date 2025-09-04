from __future__ import annotations

from typing import TYPE_CHECKING, Any

from CTFd.models import db
from cyber_skyline.chall_parser.compose.challenge_info import Question as QuestionAttr
from faker import Faker

from ng.challenge.models.Challenge import Challenge
from ng.challenge.models.ChallengeVariable import ChallengeVariable

from ...core.utils.validator import BaseValidator
import re

if TYPE_CHECKING:
    from ...team.models.Team import Team


MAX_QUESTION_NAME_LENGTH = 256
MAX_QUESTION_BODY_LENGTH = 1024
MAX_QUESTION_ANSWER_LENGTH = 512


SEED_FORMAT_STRING = "{event_id}:{challenge_id}:{question_id}:{team_seed}"


class Question(db.Model):
    __tablename__ = "ng_challenge_questions"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(MAX_QUESTION_NAME_LENGTH), nullable=False)
    body: str = db.Column(db.String(MAX_QUESTION_BODY_LENGTH), nullable=False)
    points: int = db.Column(db.Integer, nullable=False)
    templated: bool = db.Column(db.Boolean, nullable=False)
    answer: str | None = db.Column(db.String(MAX_QUESTION_ANSWER_LENGTH), nullable=True)
    answer_variable_id: int | None = db.Column(db.Integer, db.ForeignKey("ng_challenge_variables.id"), nullable=True)
    placeholder: str | None = db.Column(db.String(MAX_QUESTION_ANSWER_LENGTH), nullable=True)
    max_attempts: int = db.Column(db.Integer, nullable=False)
    challenge_id: int = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)

    challenge: Challenge = db.relationship("Challenge", back_populates="questions")
    answer_variable: ChallengeVariable | None = db.relationship("ChallengeVariable", back_populates="questions")

    def __repr__(self):
        return f"<NgChallengeQuestion {self.id}, name={self.name}, points={self.points}>"


    def serialize(self, include_admin_fields=False) -> dict[str, Any]:
        """
        Serialize the question to a dictionary.
        :return: A dictionary representation of the question.
        """
        return {
            "id": self.id,
            "name": self.name,
            "body": self.body,
            "points": self.points,
            "answer": self.answer,
            "placeholder": self.placeholder or "",
            "max_attempts": self.max_attempts,
            "challenge_id": self.challenge_id,
        }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the question data.
        :param data: The question data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        templated = data.get("templated", False)
        validator.validate_string(
            data,
            "name",
            MAX_QUESTION_NAME_LENGTH,
            required=True,
            friendly_name="Question Name",
        )
        validator.validate_string(
            data,
            "body",
            MAX_QUESTION_BODY_LENGTH,
            required=True,
            friendly_name="Question Body",
        )
        validator.validate_positive_integer(
            data,
            "points",
            required=True,
            friendly_name="Points",
        )
        validator.validate_boolean(
            data,
            "templated",
            required=True,
            friendly_name="Templated",
        )
        validator.validate_string(
            data,
            "answer",
            MAX_QUESTION_ANSWER_LENGTH,
            required=not templated,
            friendly_name="Answer",
        )
        validator.validate_model_id(
            data,
            "answer_variable_id",
            required=templated,
            friendly_name="Answer Variable ID",
        )
        validator.validate_string(
            data,
            "placeholder",
            MAX_QUESTION_ANSWER_LENGTH,
            required=False,
            friendly_name="Placeholder",
        )
        validator.validate_positive_integer(
            data,
            "max_attempts",
            required=True,
            friendly_name="Max Attempts",
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
    def create_question(
        cls,
        name: str,
        body: str,
        points: int,
        templated: bool,
        answer: str | None,
        answer_variable_id: int | None,
        max_attempts: int,
        challenge_id: int,
        placeholder: str | None = None,
        commit=True,
    ) -> Question:
        try:
            validated_data = cls.validate(
                {
                    "name": name,
                    "body": body,
                    "points": points,
                    "templated": templated,
                    "answer": answer,
                    "answer_variable_id": answer_variable_id,
                    "placeholder": placeholder,
                    "max_attempts": max_attempts,
                    "challenge_id": challenge_id,
                }
            )
            question = cls(**validated_data)
            db.session.add(question)
            db.session.flush()
            if commit:
                db.session.commit()
            return question
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_id(cls, question_id: int) -> Question | None:
        """
        Find a question by its ID.
        """
        return cls.query.filter_by(id=question_id).first()

    def check_answer(self, team: Team, answer: str) -> bool:
        """
        Check if the provided answer matches the stored answer.
        :param answer: The answer to check.
        :return: True if the answer matches, False otherwise.
        """
        # Seed faker
        faker = Faker()
        faker.seed_instance(
            SEED_FORMAT_STRING.format(
                event_id=team.event_id, challenge_id=self.challenge, question_id=self.id, team_seed=team.seed
            )
        )

        # TODO: What cleanup needs to occur on the submitted answer and is that already handled before it's passed in?

        if self.templated and isinstance(self.answer_variable, ChallengeVariable):
            variable = self.answer_variable.as_attr()
            evaluated_answer = variable.template.eval(SEED_FORMAT_STRING.format_map({
                "event_id": team.event_id,
                "challenge_id": self.challenge_id,
                "question_id": self.id,
                "team_seed": team.seed
            }))
            return evaluated_answer == answer
        elif self.answer is not None:
            return re.search(self.answer, answer) is not None

        return False

    def as_attr(self) -> QuestionAttr:
        """
        Convert the Question model to a QuestionAttr object.
        :return: A QuestionAttr object representing the question.
        """
        return QuestionAttr(
            name=self.name,  # type: ignore
            body=self.body,  # type: ignore
            points=self.points,  # type: ignore
            answer=self.answer,  # type: ignore
            max_attempts=self.max_attempts,  # type: ignore
            placeholder=self.placeholder,  # type: ignore
        )
