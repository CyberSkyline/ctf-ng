"""
A centralized utility for emitting WebSocket events via Redis pub/sub.
"""

from .logger import get_logger
from .redis_notifications import get_redis_notification_manager


logger = get_logger(__name__)


def emit_event(event_name, data, user_ids = None):
    """
    Emits a WebSocket event via Redis pub/sub

    Args:
        event_name: Name of the socket event
        data: Event data to send
        user_ids: List of specific user IDs to target, or None for broadcast
    """
    try:
        redis_manager = get_redis_notification_manager()
        if not redis_manager:
            logger.warning(
                "Redis notification manager not available. Cannot emit event."
            )
            return

        if user_ids is None:
            from ...notifications.sockets import get_connected_users
            target_user_ids = get_connected_users()
        else:
            target_user_ids = user_ids if isinstance(user_ids,
                                                     list) else [user_ids]

        if target_user_ids:
            redis_manager.publish_notification(
                user_ids = target_user_ids,
                event_name = event_name,
                data = data
            )
            logger.info(
                "Published WebSocket event '%s' for %d users.",
                event_name, len(target_user_ids)
            )
        else:
            logger.debug("No target users found for event '%s'", event_name)

    except Exception as e:
        logger.error(
            "Failed to emit WebSocket event '%s': %s",
            event_name, e,
            exc_info = True
        )


def _get_team_member_user_ids(team_id):
    """
    Get user IDs for all members of a team
    """
    try:
        from ...team.models.TeamMember import TeamMember
        members = TeamMember.query.filter_by(team_id = team_id).all()
        return [member.user_id for member in members]
    except Exception as e:
        logger.error("Error getting team members for team %s: %s", team_id, e)
        return []


def _get_event_participant_user_ids(event_id):
    """
    Get user IDs for all participants in an event
    """
    try:
        from ...team.models.TeamMember import TeamMember
        members = TeamMember.query.filter_by(event_id = event_id).all()
        return [member.user_id for member in members]
    except Exception as e:
        logger.error(
            "Error getting event participants for event %s: %s",
            event_id, e
        )
        return []


def _get_admin_user_ids():
    """
    Get user IDs for all admin users
    """
    try:
        from CTFd.models import Users
        admins = Users.query.filter_by(type = 'admin').all()
        return [admin.id for admin in admins]
    except Exception as e:
        logger.error("Error getting admin users: %s", e)
        return []


# Convenience functions
def emit_to_user(event_name, data, user_id):
    """
    Emit event to a specific user
    """
    emit_event(event_name, data, user_ids = [user_id])


def emit_to_users(event_name, data, user_ids):
    """
    Emit event to multiple specific users
    """
    emit_event(event_name, data, user_ids = user_ids)


def emit_to_team(event_name, data, team_id):
    """
    Emit event to all members of a team
    """
    user_ids = _get_team_member_user_ids(team_id)
    if user_ids:
        emit_event(event_name, data, user_ids = user_ids)


def emit_to_event(event_name, data, event_id):
    """
    Emit event to all participants in an event
    """
    user_ids = _get_event_participant_user_ids(event_id)
    if user_ids:
        emit_event(event_name, data, user_ids = user_ids)


def emit_to_admins(event_name, data):
    """
    Emit event to all admin users
    """
    user_ids = _get_admin_user_ids()
    if user_ids:
        emit_event(event_name, data, user_ids = user_ids)
