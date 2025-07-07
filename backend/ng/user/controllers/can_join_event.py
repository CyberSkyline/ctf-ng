"""
Checks if a user is eligible to join a team in a specific event.
"""

from flask import g

def can_join_event(user_id: int, event_id: int) -> bool:
    """Checks if a user can join a team in the event.

    Returns:
        dict: Success status, eligibility boolean, and reason if not eligible.
    """

    return g.user_eligibility["can_join"]
