"""
/backend/ctfd/plugin/admin/database/cleanup_orphaned_data.py
Contains the business logic for an admin tool that removes user records with no team associations.
"""

from typing import Any

from CTFd.models import db

from ...utils.logger import get_logger
from ...team.models.TeamMember import TeamMember
from ...user.models.User import User

logger = get_logger(__name__)


def cleanup_orphaned_data() -> dict[str, Any]:
    """Removes user records that have no team members."""

    orphaned_users_query = User.query.outerjoin(TeamMember, User.id == TeamMember.user_id).filter(
        TeamMember.id.is_(None)
    )

    orphaned_users = orphaned_users_query.all()
    orphaned_count = len(orphaned_users)

    if orphaned_count > 0:
        logger.info(
            "Starting orphaned data cleanup",
            extra={"context": {"orphaned_users_count": orphaned_count}},
        )

        orphaned_users_query.delete(synchronize_session=False)
        db.session.commit()

        logger.info(
            "Orphaned data cleanup completed successfully",
            extra={"context": {"cleaned_up_users": orphaned_count}},
        )
    else:
        logger.info("No orphaned data found to cleanup")

    return {
        "success": True,
        "message": "Cleanup completed successfully",
        "cleaned_up": {"orphaned_users": orphaned_count},
    }
