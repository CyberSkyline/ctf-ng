"""
/backend/ctfd/plugin/admin/database/reset_all_plugin_data.py
Contains the business logic for the destructive operation of resetting all plugin-related data.
"""

from typing import Any

from CTFd.models import db

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User
from .get_data_counts import get_data_counts

logger = get_logger(__name__)


def reset_all_plugin_data() -> dict[str, Any]:
    """Deletes all plugin data from the database.

    Returns:
        dict: Success status and deletion counts or error info.
    """

    initial_counts = get_data_counts()

    logger.warning(
        "Initiating full plugin data reset",
        extra={"context": {"initial_counts": initial_counts}},
    )

    TeamMember.query.delete()
    Team.query.delete()
    User.query.delete()
    Event.query.delete()

    db.session.commit()

    logger.info(
        "All plugin data reset successfully",
        extra={"context": {"deleted_counts": initial_counts}},
    )

    return {
        "success": True,
        "message": "All plugin data reset successfully",
        "deleted": initial_counts,
    }
