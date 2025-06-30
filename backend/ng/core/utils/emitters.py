"""
A centralized utility for emitting WebSocket events via Flask-SocketIO.
"""

from flask import current_app
from .logger import get_logger

logger = get_logger(__name__)


def emit_event(event_name, data, room=None):
    """
    Emits a WebSocket event to a specific room or to all clients.
    """
    try:
        socketio = current_app.extensions.get("socketio")
        if socketio:
            socketio.emit(event_name, data, to=room)
            logger.info(f"Emitted WebSocket event '{event_name}' to room '{room or 'all'}'.")
        else:
            logger.warning("SocketIO instance not found in app context. Cannot emit event.")
    except Exception as e:
        logger.error(f"Failed to emit WebSocket event '{event_name}': {e}", exc_info=True)
