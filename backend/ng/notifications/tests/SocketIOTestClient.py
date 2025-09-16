"""
Just wanted to thank Miguel Grinberg for the extremely detailed and *only* documentation for the SocketIOTestClient
———
""
test_client(app, namespace=None, query_string=None, headers=None, auth=None, flask_test_client=None)
The Socket.IO test client is useful for testing a Flask-SocketIO server. It works in a similar way to the Flask Test Client, but adapted to the Socket.IO server.

Parameters:
app – The Flask application instance.

namespace – The namespace for the client. If not provided, the client connects to the server on the global namespace.

query_string – A string with custom query string arguments.

headers – A dictionary with custom HTTP headers.

auth – Optional authentication data, given as a dictionary.

flask_test_client – The instance of the Flask test client currently in use. Passing the Flask test client is optional, but is necessary if you want the Flask user session and any other cookies set in HTTP routes accessible from Socket.IO events.""
""
—————
Wow. Encyclopedic!
"""

import time
import redis
import pytest
import subprocess
from datetime import timedelta
from flask_socketio import SocketIO
from flask_socketio import SocketIOTestClient

from CTFd.models import db
from CTFd.utils.security.csrf import generate_nonce

from ...core.utils import utc_now
from ...core.utils.redis_notifications import RedisNotificationManager

from ..models import Notification
from ..services import NotificationService
from .. import sockets as notification_sockets


class TestWebSocket:
    @pytest.fixture(scope = "session")
    def redis_server(self):
        """
	Start Redis server for testing
	"""
        redis_process = subprocess.Popen(
                [
                        'redis-server',
                        '--port',
                        '6381',
                        '--save',
                        '',
                        '--appendonly',
                        'no',
                        '--loglevel',
                        'warning'
                        ],
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL
                )

        time.sleep(2)

        test_client = redis.Redis(
                host = 'localhost',
                port = 6381,
                decode_responses = True
                )
        try:
            test_client.ping()
        except redis.ConnectionError:
            redis_process.terminate()
            pytest.skip("Could not start Redis server")

        yield 'redis://localhost:6381'

        redis_process.terminate()
        redis_process.wait()

    @pytest.fixture
    def redis_app(self, app, redis_server):
        """
        App configured with Redis
	"""
        original_redis_url = app.config.get('REDIS_URL')

        try:
            app.config['REDIS_URL'] = redis_server

            with app.app_context():
                from ...core.utils.redis_notifications import initialize_redis_notifications
                socketio = app.extensions.get('socketio')
                if not socketio:
                    pytest.skip("SocketIO not initialized")

                notification_sockets.initialize_notification_sockets(
                        socketio
                        )

                redis_manager = initialize_redis_notifications(socketio)
                if not redis_manager:
                    pytest.skip("Could not initialize Redis manager")

                notification_sockets.user_connections.clear()
                yield app

        finally:
            from ...core.utils.redis_notifications import get_redis_notification_manager
            current_manager = get_redis_notification_manager()
            if current_manager:
                current_manager.stop_subscriber()

            if original_redis_url:
                app.config['REDIS_URL'] = original_redis_url
            else:
                app.config.pop('REDIS_URL', None)

            notification_sockets.user_connections.clear()

    @pytest.fixture
    def authenticated_socketio_clients(self, redis_app, user, admin):
        """
        Create authenticated SocketIO clients
        """
        socketio = redis_app.extensions.get('socketio')
        if not socketio:
            pytest.skip("SocketIO not available")

        user_flask_client = redis_app.test_client()
        admin_flask_client = redis_app.test_client()

        with user_flask_client.session_transaction() as sess:
            sess.clear()
            sess['id'] = user.id
            sess['name'] = user.name
            sess['type'] = user.type
            sess['nonce'] = generate_nonce()
            sess.permanent = False

        with admin_flask_client.session_transaction() as sess:
            sess.clear()
            sess['id'] = admin.id
            sess['name'] = admin.name
            sess['type'] = admin.type
            sess['nonce'] = generate_nonce()
            sess.permanent = False

        user_socketio_client = SocketIOTestClient(
                redis_app,
                socketio,
                flask_test_client = user_flask_client
                )

        admin_socketio_client = SocketIOTestClient(
                redis_app,
                socketio,
                flask_test_client = admin_flask_client
                )

        clients = {
                'user': user_socketio_client,
                'admin': admin_socketio_client,
                'user_flask': user_flask_client,
                'admin_flask': admin_flask_client
                }

        yield clients

        for key, client in clients.items():
            if 'flask' not in key and hasattr(client,
                                              'connected'
                                              ) and client.connected:
                client.disconnect()

        notification_sockets.user_connections.clear()

    def test_full_refetch_pipeline_with_auth(
            self,
            authenticated_socketio_clients,
            user,
            ticket,
            redis_app
            ):
        """
        Test complete authenticated refetch pipeline
        """
        user_client = authenticated_socketio_clients['user']

        assert user_client.is_connected()
        user_client.get_received()

        with redis_app.app_context():
            NotificationService._emit_refetch(
                    path = f"/ng/support/tickets/{ticket.id}",
                    user_ids = [user.id]
                    )

        time.sleep(1.0)

        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) > 0, f"Expected refetch event, got: {received}"
        assert refetch_events[0]['args'][0][
                'path'] == f"/ng/support/tickets/{ticket.id}"

    def test_notification_service_full_flow(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            ticket,
            redis_app
            ):
        """
        Test NotificationService creates both DB notification and WebSocket events
        """
        user_client = authenticated_socketio_clients['user']

        assert user_client.is_connected()
        user_client.get_received()

        with redis_app.app_context():
            NotificationService.notify_ticket_reply(
                    ticket_id = ticket.id,
                    author_id = admin.id,
                    recipient_id = user.id,
                    is_admin_reply = True
                    )

            notifications = Notification.find_filtered_notifications(
                    recipient_id = user.id
                    )
            ticket_notifications = [
                    n for n in notifications if n.ticket_id == ticket.id
                    ]
            assert len(ticket_notifications) > 0, "Should create DB notification"

        time.sleep(1.0)

        received = user_client.get_received()
        notification_events = [
                e for e in received if e.get('name') == 'notification'
                ]
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(notification_events) > 0, "Should receive notification WebSocket event"
        assert len(refetch_events) > 0, "Should receive refetch WebSocket event"

    def test_cross_instance_coordination_with_auth(
            self,
            authenticated_socketio_clients,
            user,
            redis_app,
            redis_server
            ):
        """
        Test multi instance coordination through Redis with authenticated clients
        """
        user_client = authenticated_socketio_clients['user']
        assert user_client.is_connected()
        user_client.get_received()

        instance2_socketio = SocketIO()

        instance2_manager = RedisNotificationManager(
                socketio = instance2_socketio
                )
        instance2_manager.redis_client = redis.from_url(
                redis_server,
                decode_responses = True
                )

        received_messages = []
        instance2_manager._handle_notification_message = lambda msg: received_messages.append(
                msg
                )

        instance2_manager.start_subscriber()
        time.sleep(0.5)

        try:
            with redis_app.app_context():
                NotificationService._emit_refetch(
                        path = "/test/cross/instance",
                        user_ids = [user.id]
                        )

            time.sleep(1.0)

            assert len(received_messages) > 0, "Instance2 should receive message via Redis"

            received = user_client.get_received()
            refetch_events = [
                    e for e in received if e.get('name') == 'refetch'
                    ]
            assert len(refetch_events) > 0, "Instance1 client should receive message"

        finally:
            instance2_manager.stop_subscriber()

    def test_team_broadcast_with_auth(
            self,
            authenticated_socketio_clients,
            user,
            team_with_member,
            redis_app
            ):
        """
        Test team broadcasts with authenticated clients
        """
        user_client = authenticated_socketio_clients['user']
        assert user_client.is_connected()
        user_client.get_received()

        with redis_app.app_context():
            NotificationService._emit_refetch(
                    path = f"/ng/teams/{team_with_member.id}",
                    team_id = team_with_member.id
                    )

        time.sleep(1.0)

        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) > 0, "Team member should receive team broadcast"

    def test_unauthenticated_connection_rejected(self, redis_app):
        """
        Test that connections without authenticated Flask session are rejected
        """
        socketio = redis_app.extensions.get('socketio')

        unauthenticated_flask_client = redis_app.test_client()

        unauthenticated_socketio_client = SocketIOTestClient(
                redis_app,
                socketio,
                flask_test_client = unauthenticated_flask_client
                )

        connected = unauthenticated_socketio_client.is_connected()
        assert not connected, "Unauthenticated connection should be rejected"

    def test_connection_lifecycle_with_auth(
            self,
            authenticated_socketio_clients,
            user,
            redis_app
            ):
        """
        Test connection lifecycle with auth
        """
        user_client = authenticated_socketio_clients['user']

        notification_sockets.user_connections.clear()
        assert user.id not in notification_sockets.user_connections

        assert user_client.is_connected()

        user_client.disconnect()
        time.sleep(0.1)
        user_client.connect()
        time.sleep(0.5)

        assert user.id in notification_sockets.user_connections

        user_client.get_received()

        with redis_app.app_context():
            NotificationService._emit_refetch(
                    path = "/test/lifecycle",
                    user_ids = [user.id]
                    )

        time.sleep(1.0)
        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]
        assert len(refetch_events) > 0, "Should receive message while connected"

        user_client.disconnect()
        time.sleep(0.1)

        assert (user.id not in notification_sockets.user_connections or
                len(notification_sockets.user_connections[user.id]) == 0), \
                      "Should be removed from tracking after disconnect"

    def test_create_ticket_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            event,
            team_with_member,
            redis_app
            ):
        """
        Test create_ticket controller with WebSocket notifications
        """
        admin_client = authenticated_socketio_clients['admin']
        user_flask = authenticated_socketio_clients['user_flask']

        assert admin_client.is_connected()
        admin_client.get_received()

        response = user_flask.post(
                "/ng/support/tickets/create",
                json = {
                        "subject": "WebSocket Test Ticket",
                        "text": "Testing real socket integration",
                        "event_id": event.id,
                        },
                )

        assert response.status_code == 201
        time.sleep(1.0)

        received = admin_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) > 0, f"Expected refetch event, got: {received}"
        assert "/ng/support/tickets" in refetch_events[0]['args'][0]['path'
                                                                     ]

    def test_submit_answer_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            redis_app,
            challenge_factory,
            question_factory,
            team_with_member
            ):
        """
        Test submit_answer controller with WebSocket notifications
        """
        user_client = authenticated_socketio_clients['user']
        user_flask = authenticated_socketio_clients['user_flask']

        challenge = challenge_factory(event_id = team_with_member.event_id)
        question = question_factory(challenge_id = challenge.id)

        event_id = challenge.event_id
        challenge_id = challenge.id
        question_id = question.id
        answer = question.answer

        with redis_app.app_context():

            db.session.add(team_with_member)
            team_with_member.set_start_timestamp(
                    utc_now() - timedelta(hours = 1)
                    )

        assert user_client.is_connected()
        user_client.get_received()

        response = user_flask.post(
                f"/ng/events/{event_id}/challenges/{challenge_id}/questions/{question_id}/submit",
                json = {"submission": answer},
                )

        assert response.status_code == 201
        time.sleep(1.0)

        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) >= 2, f"Expected at least 2 refetch events, got: {received}"
        paths = [event['args'][0]['path'] for event in refetch_events]
        assert any(f"/challenges/{challenge_id}" in path for path in paths), f"Expected challenge path in: {paths}"
        assert any("/leaderboard" in path for path in paths), f"Expected leaderboard path in: {paths}"

    def test_redeem_hint_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            redis_app,
            challenge_factory,
            hint_factory,
            team_with_member
            ):
        """
        Test redeem_hint controller with WebSocket notifications
        """
        user_client = authenticated_socketio_clients['user']
        user_flask = authenticated_socketio_clients['user_flask']

        challenge = challenge_factory(event_id = team_with_member.event_id)
        hint = hint_factory(challenge_id = challenge.id)

        event_id = challenge.event_id
        challenge_id = challenge.id
        hint_id = hint.id

        with redis_app.app_context():
            db.session.add(team_with_member)
            team_with_member.set_start_timestamp(
                    utc_now() - timedelta(hours = 1)
                    )

        assert user_client.is_connected()
        user_client.get_received()

        with user_flask.session_transaction() as sess:
            nonce = sess.get("nonce")

        response = user_flask.post(
                f"/ng/events/{event_id}/challenges/{challenge_id}/hint/{hint_id}/redeem",
                data = {"nonce": nonce}
                )

        assert response.status_code == 201
        time.sleep(1.0)

        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) > 0, f"Expected refetch event, got: {received}"
        assert f"/challenges/{challenge_id}" in refetch_events[0]['args'][
                0]['path']

    def test_create_ticket_message_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            ticket,
            redis_app
            ):
        """
        Test create_ticket_message controller with WebSocket notifications
        """
        user_client = authenticated_socketio_clients['user']
        admin_flask = authenticated_socketio_clients['admin_flask']

        assert user_client.is_connected()
        user_client.get_received()

        response = admin_flask.post(
                f"/ng/admin/support/tickets/{ticket.id}/add_message",
                json = {"text": "Admin response via WebSocket test"},
                )

        assert response.status_code == 201
        time.sleep(1.0)

        received = user_client.get_received()
        notification_events = [
                e for e in received if e.get('name') == 'notification'
                ]
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(notification_events) > 0, f"Expected notification event, got: {received}"
        assert len(refetch_events) > 0, f"Expected refetch event, got: {received}"
        assert f"/tickets/{ticket.id}" in refetch_events[0]['args'][0][
                'path']

    def test_update_ticket_status_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            ticket,
            redis_app
            ):
        """
        Test update_ticket_status controller with real WebSocket notifications
        """
        user_client = authenticated_socketio_clients['user']
        admin_flask = authenticated_socketio_clients['admin_flask']

        assert user_client.is_connected()
        user_client.get_received()

        response = admin_flask.put(
                f"/ng/admin/support/tickets/{ticket.id}/close",
                json = {"closed": True},
                )

        assert response.status_code == 200
        time.sleep(1.0)

        received = user_client.get_received()
        notification_events = [
                e for e in received if e.get('name') == 'notification'
                ]

        assert len(notification_events) > 0, f"Expected notification event, got: {received}"
        notif_data = notification_events[0]['args'][0]
        assert "closed" in notif_data['message'].lower()

    def test_multi_user_ticket_workflow_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            event,
            team_with_member,
            redis_app
            ):
        """
        Test complete ticket workflow with multiple users and real WebSockets
        """
        user_client = authenticated_socketio_clients['user']
        admin_client = authenticated_socketio_clients['admin']
        user_flask = authenticated_socketio_clients['user_flask']
        admin_flask = authenticated_socketio_clients['admin_flask']

        user_client.get_received()
        admin_client.get_received()

        response = user_flask.post(
                "/ng/support/tickets/create",
                json = {
                        "subject": "Multi-user WebSocket Test",
                        "text": "Initial ticket message",
                        "event_id": event.id,
                        },
                )

        assert response.status_code == 201
        ticket_id = response.get_json()["data"]["id"]
        time.sleep(1.0)

        admin_received = admin_client.get_received()
        admin_refetch = [
                e for e in admin_received if e.get('name') == 'refetch'
                ]
        assert len(admin_refetch) > 0, f"Admin should receive ticket creation, got: {admin_received}"

        admin_flask.post(
                f"/ng/admin/support/tickets/{ticket_id}/add_message",
                json = {"text": "Admin response"},
                )
        time.sleep(1.0)

        user_received = user_client.get_received()
        user_notifications = [
                e for e in user_received if e.get('name') == 'notification'
                ]
        user_refetch = [
                e for e in user_received if e.get('name') == 'refetch'
                ]

        assert len(user_notifications) > 0, f"User should receive admin reply notification, got: {user_received}"
        assert len(user_refetch) > 0, f"User should receive refetch event, got: {user_received}"

        admin_flask.put(
                f"/ng/admin/support/tickets/{ticket_id}/close",
                json = {"closed": True},
                )
        time.sleep(1.0)

        final_user_received = user_client.get_received()
        status_notifications = [
                e for e in final_user_received
                if e.get('name') == 'notification'
                ]

        assert len(status_notifications) > 0, f"User should receive status change notification, got: {final_user_received}"
        assert "closed" in status_notifications[0]['args'][0]['message'
                                                              ].lower()

    def test_concurrent_answer_submissions_with_real_websockets(
            self,
            authenticated_socketio_clients,
            user,
            redis_app,
            challenge_factory,
            question_factory,
            team_with_member
            ):
        """
        Test multiple rapid answer submissions with WebSocket coordination
        """
        user_client = authenticated_socketio_clients['user']
        user_flask = authenticated_socketio_clients['user_flask']

        challenge = challenge_factory(event_id = team_with_member.event_id)
        question = question_factory(challenge_id = challenge.id)

        event_id = challenge.event_id
        challenge_id = challenge.id
        question_id = question.id

        with redis_app.app_context():
            db.session.add(team_with_member)
            team_with_member.set_start_timestamp(
                    utc_now() - timedelta(hours = 1)
                    )

        assert user_client.is_connected()
        user_client.get_received()

        responses = []
        for i in range(3):
            response = user_flask.post(
                    f"/ng/events/{event_id}/challenges/{challenge_id}/questions/{question_id}/submit",
                    json = {"submission": f"wrong_answer_{i}"},
                    )
            responses.append(response)

        for response in responses:
            assert response.status_code == 201

        time.sleep(1.5)

        received = user_client.get_received()
        refetch_events = [
                e for e in received if e.get('name') == 'refetch'
                ]

        assert len(refetch_events) >= 3, f"Expected at least 3 refetch events for rapid submissions, got: {len(refetch_events)}"

    def test_notification_service_integration_with_controllers(
            self,
            authenticated_socketio_clients,
            user,
            admin,
            event,
            team_with_member,
            redis_app
            ):
        """
        Test that NotificationService properly integrates with controller actions
        """
        user_client = authenticated_socketio_clients['user']
        admin_client = authenticated_socketio_clients['admin']
        user_flask = authenticated_socketio_clients['user_flask']
        admin_flask = authenticated_socketio_clients['admin_flask']

        user_client.get_received()
        admin_client.get_received()

        response = user_flask.post(
                "/ng/support/tickets/create",
                json = {
                        "subject": "Service Integration Test",
                        "text": "Testing service integration",
                        "event_id": event.id,
                        },
                )

        assert response.status_code == 201
        ticket_id = response.get_json()["data"]["id"]
        time.sleep(1.0)

        admin_received = admin_client.get_received()
        assert len(admin_received) > 0, "Admin should receive WebSocket events from NotificationService"

        admin_flask.put(
                f"/ng/admin/support/tickets/{ticket_id}/assign",
                json = {"user_id": admin.id},
                )
        time.sleep(1.0)

        admin_flask.post(
                f"/ng/admin/support/tickets/{ticket_id}/add_message",
                json = {"text": "I'll help you with this"},
                )
        time.sleep(1.0)

        user_received = user_client.get_received()
        user_notifications = [
                e for e in user_received if e.get('name') == 'notification'
                ]

        assert len(user_notifications) > 0, "User should receive admin reply notification via WebSocket"

        with redis_app.app_context():
            notifications = Notification.find_filtered_notifications(
                    recipient_id = user.id
                    )
            ticket_notifications = [
                    n for n in notifications if n.ticket_id == ticket_id
                    ]
            assert len(ticket_notifications) > 0, "Notification should be stored in database"
