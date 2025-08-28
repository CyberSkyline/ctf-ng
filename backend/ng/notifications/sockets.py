"""
WebSocket handlers for notification rooms
Manages user/team/event room subscriptions for updates
"""

from flask_socketio import join_room, leave_room

from CTFd.utils.user import get_current_user

from ..core.utils.logger import get_logger

from ..user.models import User
from ..team.models import Team


logger = get_logger(__name__)


def initialize_notification_sockets(socketio):
    """
    Initialize WebSocket handlers for notifications
    """
    @socketio.on("subscribe_notifications")
    def handle_subscribe():
        """
        Subscribe user to their notification channels
        """
        user = get_current_user()
        if not user:
            return False

        ng_user = User.find_or_create_by_ctfd_id(user.id)

        user_room = f"user_{user.id}"
        join_room(user_room)
        logger.debug(f"User {user.id} joined room {user_room}")

        for team_member in ng_user.team_members:
            team_room = f"team_{team_member.team_id}"
            join_room(team_room)
            logger.debug(f"User {user.id} joined room {team_room}")

            event_room = f"event_{team_member.event_id}"
            join_room(event_room)
            logger.debug(f"User {user.id} joined room {event_room}")

        return True

    @socketio.on("unsubscribe_notifications")
    def handle_unsubscribe():
        """
        Unsubscribe from notification channels
        """
        user = get_current_user()
        if not user:
            return False

        ng_user = User.find_by_id(user.id)
        if not ng_user:
            return False

        user_room = f"user_{user.id}"
        leave_room(user_room)

        for team_member in ng_user.team_members:
            leave_room(f"team_{team_member.team_id}")
            leave_room(f"event_{team_member.event_id}")

        return True

    @socketio.on("join_event")
    def handle_join_event(data):
        """
        Join event room for updates
        """
        user = get_current_user()
        if not user:
            return False

        event_id = data.get("event_id")
        if not event_id:
            return False

        team = Team.find_by_user_and_event(user.id, event_id)
        if not team:
            return False

        room = f"event_{event_id}"
        join_room(room)
        logger.debug(f"User {user.id} joined event room {room}")

        return True
