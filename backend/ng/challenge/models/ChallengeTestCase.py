from typing import Any

from CTFd.models import db

from ...core.utils.validator import BaseValidator
from .Question import MAX_QUESTION_ANSWER_LENGTH


class QuestionTestCase(db.Model):
    __tablename__ = "ng_question_test_cases"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("ng_challenge_questions.id"), nullable=False, index=True)
    answer = db.Column(db.String(MAX_QUESTION_ANSWER_LENGTH), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)

    question = db.relationship("Question", back_populates="test_cases")

    def __repr__(self):
        return f"<NgQuestionTestCase {self.id}, question_id={self.question_id}, answer={self.answer}, correct={self.correct}>"

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
            "answer",
            MAX_QUESTION_ANSWER_LENGTH,
            required=True,
            friendly_name="Answer",
        )
        validator.validate_model_id(
            data,
            "question_id",
            "Question",
            required=True,
            friendly_name="Question ID",
        )
        validator.validate_boolean(
            data,
            "correct",
            required=True,
            friendly_name="Correct",
        )

        return validator.validate()

    @classmethod
    def create_test_case(cls, question_id: int, answer: str, correct: bool, commit=True):
        try:
            validated_data = cls.validate({"answer": answer, "question_id": question_id, "correct": correct})

            test_case = cls(**validated_data)
            db.session.add(test_case)
            db.session.flush()

            if commit:
                db.session.commit()
            return test_case
        except Exception as e:
            db.session.rollback()
            raise e
