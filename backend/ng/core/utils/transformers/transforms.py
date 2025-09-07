from .base import HasTransform, ValidatorResult, Success, Failure
from datetime import datetime, UTC

class ToNaiveDatetime(HasTransform[str]):
    def __init__(self, future_only: bool = False) -> None:
        self.future_only = future_only

    def transform(self, value: str) -> ValidatorResult[datetime]:
        result = None
        try:
            result = datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return Failure("{field} must be a valid datetime in ISO format (YYYY-MM-DDTHH:MM:SS)")

        if result.tzinfo is not UTC:
            return Failure("{field} must be specified in UTC (Z or +00:00)")

        if self.future_only and result < datetime.now(UTC):
            return Failure("{field} must be in the future")

        return Success(result)