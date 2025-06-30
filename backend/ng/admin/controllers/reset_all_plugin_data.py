"""
Contains the business logic for the
destructive operation of resetting all plugin related data.
"""

from typing import Any

from ...event.models.Event import Event
from .get_data_counts import get_data_counts


def reset_all_plugin_data() -> dict[str, Any]:
    """Deletes all plugin data from the database."""
    initial_counts = get_data_counts()

    Event.reset_all_plugin_data()

    return {
        "message": "All plugin data reset successfully",
        "deleted": initial_counts,
    }
