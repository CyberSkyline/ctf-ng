"""
Contains the business logic for an admin tool
that removes user records with no team associations.
"""

from typing import Any

from ...user.models.User import User


def cleanup_orphaned_data() -> dict[str, Any]:
    """Removes user records that have no team members."""
    orphaned_count = User.cleanup_orphaned_users()

    return {
        "message": "Cleanup completed successfully",
        "cleaned_up": {"orphaned_users": orphaned_count},
    }
