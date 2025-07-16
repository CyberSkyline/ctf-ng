from __future__ import annotations

from typing import Any

from CTFd.models import db

from ...core.validation import BaseValidator

MAX_QUESTION_NAME_LENGTH = 256
MAX_QUESTION_BODY_LENGTH = 1024
MAX_QUESTION_ANSWER_LENGTH = 512


class Question(db.Model):
    __tablename__ = "ng_challenge_questions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_QUESTION_NAME_LENGTH), nullable=False)
    body = db.Column(db.String(MAX_QUESTION_BODY_LENGTH), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(MAX_QUESTION_ANSWER_LENGTH), nullable=False)
    max_attempts = db.Column(db.Integer, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)

    challenge = db.relationship("Challenge", back_populates="questions")

    def __repr__(self):
        return f"<NgChallengeQuestion {self.id}, name={self.name}, points={self.points}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the question data.
        :param data: The question data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

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
        validator.validate_string(
            data,
            "answer",
            MAX_QUESTION_ANSWER_LENGTH,
            required=True,
            friendly_name="Answer",
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
        cls, name: str, body: str, points: int, answer: str, max_attempts: int, challenge_id: int, commit=True
    ) -> Question:
        try:
            validated_data = cls.validate(
                {
                    "name": name,
                    "body": body,
                    "points": points,
                    "answer": answer,
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

    def check_answer(self, answer: str, team) -> bool:
        """
        Check if the provided answer matches the stored answer.
        :param answer: The answer to check.
        :return: True if the answer matches, False otherwise.
        """
        return False
        # return self.answer.strip().lower() == answer.strip().lower()
