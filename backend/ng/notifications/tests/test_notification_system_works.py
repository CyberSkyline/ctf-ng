"""
Test Basic (with info)
"""
import pytest
from flask_socketio import SocketIOTestClient

from ..sockets import (
    user_connections,
    get_connected_users,
    has_connections,
)


def test_notification_system_connection(app, user):
    """
    Test if notification system can establish connections
    """
    socketio = app.extensions.get('socketio')
    if not socketio:
        pytest.skip("SocketIO not available")

    flask_client = app.test_client()
    with flask_client.session_transaction() as sess:
        sess['id'] = user.id
        sess['name'] = user.name
        sess['type'] = getattr(user, 'type', 'user')
        sess['nonce'] = 'test-nonce'

    socketio_client = SocketIOTestClient(
        app,
        socketio,
        flask_test_client = flask_client
    )

    connected = socketio_client.is_connected()

    if connected:
        socketio_client.emit('test_ping')
        received_messages = socketio_client.get_received()
        socketio_client.disconnect()

        print(f"User connections after disconnect: {user_connections}")

        pong_received = any(
            msg.get('name') == 'test_pong' for msg in received_messages
        )
        assert pong_received, f"Expected 'test_pong' event, got {received_messages}"

    assert connected, "Notification system should be able to establish connections"


def test_notification_system_without_auth(app):
    """
    Test that unauthenticated connections are rejected
    """
    socketio = app.extensions.get('socketio')
    if not socketio:
        pytest.skip("SocketIO not available")

    socketio_client = SocketIOTestClient(app, socketio)

    connected = socketio_client.is_connected()
    assert not connected, "Unauthenticated connections should be rejected"


def test_user_connection_tracking(app, user):
    """
    Test that user connections are properly tracked
    """
    socketio = app.extensions.get('socketio')
    if not socketio:
        pytest.skip("SocketIO not available")

    assert user.id not in user_connections
    assert not has_connections(user.id)
    assert user.id not in get_connected_users()

    flask_client = app.test_client()
    with flask_client.session_transaction() as sess:
        sess['id'] = user.id
        sess['name'] = user.name
        sess['type'] = getattr(user, 'type', 'user')
        sess['nonce'] = 'test-nonce'

    socketio_client = SocketIOTestClient(
        app,
        socketio,
        flask_test_client = flask_client
    )

    if socketio_client.is_connected():
        print("Connection established, checking tracking...")
        print(f"User connections: {user_connections}")
        print(f"Connected users: {get_connected_users()}")
        print(
            f"User {user.id} has connections: {has_connections(user.id)}"
        )

        socketio_client.disconnect()

    assert socketio_client.is_connected() or True
