"""
Delete an attempt and its associated score event
"""

from ...models import Attempt


def delete_attempt(attempt: Attempt) -> None:
    """
    Delete an attempt and adjust team score accordingly

    Args:
        attempt: The attempt to delete
    """
    attempt.delete_attempt(commit=True)
