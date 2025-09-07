"""
Validators for the transformer pipeline which have the implicit assumption that any transformer in here
does not change the data in any way.
"""
from enum import Enum
from typing import Any

from .base import HasTransform, ValidatorResult, Success, Failure

from CTFd.models import db, Users

class NotNone(HasTransform[Any]):
    def __init__(self, required: bool = True) -> None:
        self.required = required

    def transform(self, value: Any) -> ValidatorResult[Any]:
        if self.required and value is None:
            return Failure("{field} is required")
        return Success(value)

class NotEmpty(HasTransform[str]):
    def transform(self, value: str | list | dict) -> ValidatorResult[str | list | dict]:
        if (value is None or len(value.strip()) == 0):
            return Failure("{field} cannot be empty")
        return Success(value)

class MinLen(HasTransform[str | list | dict]):
    def __init__(self, min_len: int):
        self.min_len = min_len

    def transform(self, value: str | list | dict) -> ValidatorResult[str | list | dict]:
        if len(value) < self.min_len:
            return Failure("Length of {field} is {actual} but must be at least {min_len}", actual=str(len(value)), min_len=str(self.min_len))
        return Success(value)

class MaxLen(HasTransform[str | list | dict]):
    def __init__(self, max_len: int):
        self.max_len = max_len

    def transform(self, value: str | list | dict) -> ValidatorResult[str | list | dict]:
        if len(value) > self.max_len:
            return Failure("Length of {field} is {actual} but must be at most {max_len}", actual=str(len(value)), max_len=str(self.max_len))
        return Success(value)

class ForeignKeyExists[T: db.Model](HasTransform[int]):
    def __init__(self, model: type[T], field: str = "id"):
        self.model = model
        self.field = field

    def transform(self, value: int) -> ValidatorResult[int]:
        exists = self.model.query.filter(getattr(self.model, self.field) == value).first()
        if not exists:
            return Failure("{field} with id {id} does not exist", id=str(value))
        return Success(value)

class MinValue(HasTransform[int | float]):
    def __init__(self, min_value: int | float):
        self.min_value = min_value

    def transform(self, value: int | float) -> ValidatorResult[int | float]:
        if value < self.min_value:
            return Failure("{field} is {actual} but must be at least {min_value}", actual=str(value), min_value=str(self.min_value))
        return Success(value)

class MaxValue(HasTransform[int | float]):
    def __init__(self, max_value: int | float):
        self.max_value = max_value

    def transform(self, value: int | float) -> ValidatorResult[int | float]:
        if value > self.max_value:
            return Failure("{field} is {actual} but must be at most {max_value}", actual=str(value), max_value=str(self.max_value))
        return Success(value)

class InRange(HasTransform[int | float]):
    def __init__(self, min_value: int | float, max_value: int | float):
        self.min_value = min_value
        self.max_value = max_value

    def transform(self, value: int | float) -> ValidatorResult[int | float]:
        if value < self.min_value or value > self.max_value:
            return Failure("{field} is {actual} but must be between {min_value} and {max_value}", actual=str(value), min_value=str(self.min_value), max_value=str(self.max_value))
        return Success(value)

class NonZero(HasTransform[int | float]):
    def transform(self, value: int | float) -> ValidatorResult[int | float]:
        if value == 0:
            return Failure("{field} cannot be zero")
        return Success(value)

class InEnum(HasTransform[str | int]):
    def __init__(self, enum: type[Enum]):
        self.enum = enum

    def transform(self, value: str | int) -> ValidatorResult[str | int]:
        try:
            if isinstance(value, str):
                self.enum[value]
            else:
                self.enum(value)
            return Success(value)
        except (KeyError, ValueError):
            return Failure("{field} must be one of {enum_values}", enum_values=', '.join([member.name for member in self.enum]))

class Positive(MinValue):
    def __init__(self):
        super().__init__(1)

class RequireAdmin(HasTransform[int]):
    def transform(self, value: int) -> ValidatorResult[int]:
        user = Users.query.get(value)
        if not user:
            return Failure("{field} with ID {id} does not exist", id=str(value))

        if user.type != 'admin':
            return Failure("User must be an admin to perform this action")
        return Success(value)