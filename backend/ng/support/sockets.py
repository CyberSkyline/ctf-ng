"""
Defines all Flask-SocketIO event handlers for the real time support system.
VERY BASIC (no auth, rate limiting - has verbose logging for now, etc etc.)
"""

from flask_socketio import join_room, leave_room, emit
from ..core.utils import get_logger

logger = get_logger(__name__)


def initialize_socket_handlers(socketio):
    """
    Registers all socket event handlers with the main SocketIO instance.

    Args:
        socketio: The Flask-SocketIO server instance.
    """

    @socketio.on("connect")  # Debugging
    def handle_connect():
        logger.info("Client connected successfully.")
        emit("connection_ack", {"message": "You are connected to the support socket."})

    @socketio.on("disconnect")  # Debugging
    def handle_disconnect():
        logger.info("Client disconnected.")

    @socketio.on("join_ticket_room")
    def handle_join_ticket_room(data):
        """
        Allows a client to subscribe to real time updates for a specific ticket.
        The client should send this event when they open a ticket page.

        Expected data: {'ticket_id': 123}
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                emit("error", {"message": "ticket_id is required to join a room."})
                return

            room_name = f"ticket_{ticket_id}"
            join_room(room_name)
            logger.info(f"Client joined room: {room_name}")
            emit("room_joined", {"room": room_name, "status": "success"})
        except Exception as e:
            logger.error(f"Error in handle_join_ticket_room: {e}", exc_info=True)
            emit(
                "error",
                {"message": "An internal error occurred while joining the room."},
            )

    @socketio.on("leave_ticket_room")
    def handle_leave_ticket_room(data):
        """
        Allows a client to unsubscribe from a ticket's updates.
        The client should send this when they navigate away from a ticket page.

        Expected data: {'ticket_id': 123}
        """
        try:
            ticket_id = data.get("ticket_id")
            if not ticket_id:
                emit("error", {"message": "ticket_id is required to leave a room."})
                return

            room_name = f"ticket_{ticket_id}"
            leave_room(room_name)
            logger.info(f"Client left room: {room_name}")
            emit("room_left", {"room": room_name, "status": "success"})
        except Exception as e:
            logger.error(f"Error in handle_leave_ticket_room: {e}", exc_info=True)
            emit(
                "error",
                {"message": "An internal error occurred while leaving the room."},
            )

    @socketio.on("user_is_typing")
    def handle_user_typing(data):
        """
        Broadcasts that a user is typing a message in a specific ticket.

        Expected data: {'ticket_id': 123, 'user_name': 'testuser'}
        """
        try:
            ticket_id = data.get("ticket_id")
            user_name = data.get("user_name", "A user")
            if not ticket_id:
                return

            room_name = f"ticket_{ticket_id}"
            emit(
                "typing_start",
                {"user_name": user_name},
                to=room_name,
                include_self=False,
            )
        except Exception as e:
            logger.error(f"Error in handle_user_typing: {e}", exc_info=True)

    @socketio.on("user_stops_typing")
    def handle_user_stops_typing(data):
        """
        Broadcasts that a user has stopped typing.

        Expected data: {'ticket_id': 123, 'user_name': 'testuser'}
        """
        try:
            ticket_id = data.get("ticket_id")
            user_name = data.get("user_name", "A user")
            if not ticket_id:
                return

            room_name = f"ticket_{ticket_id}"
            emit(
                "typing_stop",
                {"user_name": user_name},
                to=room_name,
                include_self=False,
            )
        except Exception as e:
            logger.error(f"Error in handle_user_stops_typing: {e}", exc_info=True)
