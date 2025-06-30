"""
Calculates participation statistics for a user across all events.
"""

from flask import g
from typing import Any


def get_user_stats(user_id: int) -> dict[str, Any]:
    """Gets participation stats for a user across all events.

    Returns:
        dict: Participation stats.
    """
    stats = g.user_stats

    return {"stats": stats}
