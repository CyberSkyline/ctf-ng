"""
WebSocket handlers for notification system with Redis pub/sub
Manages user connections without using socket.io rooms
"""

from flask import request
from flask_socketio import disconnect, emit

from CTFd.utils.user import get_current_user

from ..core.utils.logger import get_logger


logger = get_logger(__name__)

# Global lookup table: user_id -> [socket_session_ids]
user_connections = {}


def initialize_notification_sockets(socketio):
    """
    Initialize WebSocket handlers for notifications with Redis pub/sub
    """
    @socketio.on("connect")
    def handle_connect():
        """
        Handle new socket connection - add to user lookup table
        """
        user = get_current_user()

        if not user:
            logger.warning("Unauthenticated connection attempt")
            disconnect()
            return False

        if user.id not in user_connections:
            user_connections[user.id] = []

        user_connections[user.id].append(request.sid)
        logger.debug(
            "User %s connected with SID %s. Total connections: %d",
            user.id, request.sid, len(user_connections[user.id])
        )
        return True

    @socketio.on("disconnect")
    def handle_disconnect():
        """
        Handle socket disconnection - remove from user lookup table
        """
        user = get_current_user()
        if user and user.id in user_connections:

            user_connections[user.id] = [
                sid for sid in user_connections[user.id] if sid != request.sid
            ]

            if not user_connections[user.id]:
                del user_connections[user.id]

            logger.debug(
                "User %s disconnected. Remaining connections: %d",
                user.id, len(user_connections.get(user.id, []))
            )

    @socketio.on("ping")
    def handle_ping():
        """
        Simple ping/pong for connection health checks
        """
        return "pong"

    @socketio.on("test_ping")
    def handle_test_ping():
        """
        Test-specific ping that emits response for test verification
        """
        emit("test_pong")

def get_connected_users():
    """
    Get list of currently connected user IDs
    """
    return list(user_connections.keys())


def get_user_connections(user_id):
    """
    Get socket session IDs for a specific user
    """
    return user_connections.get(user_id, [])


def has_connections(user_id):
    """
    Check if a user has any active connections
    """
    return user_id in user_connections and len(user_connections[user_id]) > 0
