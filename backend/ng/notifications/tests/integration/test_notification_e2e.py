"""
Basic E2E Testing
"""

import re
import time
import pytest
import requests
import socketio
from queue import Queue, Empty
from ....config import CTFD_BASE_URL


class TestExternalIntegration:
    """
    Tests that run outside Docker
    """
    def test_ctfd_is_running(self):
        """
        Verify CTFd is accessible
        """
        resp = requests.get(f"{CTFD_BASE_URL}/")
        assert resp.status_code == 200

    def test_api_accessible(self):
        """
        Verify API is working
        """
        resp = requests.get(f"{CTFD_BASE_URL}/api/v1/users")
        assert resp.status_code == 200

    def test_create_user_and_login(self):
        """
        Test user creation and login flow
        """
        session = requests.Session()

        user_data = {
            "name": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }

        session.post(
            f"{CTFD_BASE_URL}/api/v1/users",
            json = user_data
        )

        login_response = session.post(
            f"{CTFD_BASE_URL}/ng/users/login",
            json = {
                "username": "testuser",
                "password": "testpass123"
            }
        )

        assert login_response.status_code == 200
        assert session.cookies.get('session') is not None

    def test_websocket_with_auth(self):
        """
        Test WebSocket connection with authentication
        """
        session = requests.Session()

        try:
            session.post(f"{CTFD_BASE_URL}/reset", timeout = 5)
        except Exception:
            pass

        credentials_to_try = [
            ("admin",
             "ctfng_password"),
            ("admin",
             "admin123"),
            ("admin",
             "password")
        ]

        login_page = session.get(f"{CTFD_BASE_URL}/login")

        csrf_token = None
        if "csrf_token" in login_page.text or "nonce" in login_page.text:
            csrf_match = re.search(
                r'name="nonce" value="([^"]+)"',
                login_page.text
            )
            if not csrf_match:
                alt_patterns = [
                    r'name=["\']nonce["\'] value=["\']([^"\']+)["\']',
                    r'<input[^>]*name=["\']nonce["\'][^>]*value=["\']([^"\']+)["\']',
                    r'"nonce":\s*"([^"]+)"'
                ]
                for pattern in alt_patterns:
                    csrf_match = re.search(pattern, login_page.text)
                    if csrf_match:
                        break

            if csrf_match:
                csrf_token = csrf_match.group(1)
            else:
                pass

        successful_login = False
        for attempt_user, attempt_pass in credentials_to_try:

            login_data = {"name": attempt_user, "password": attempt_pass}
            if csrf_token:
                login_data["nonce"] = csrf_token

            login_resp = session.post(
                f"{CTFD_BASE_URL}/login",
                data = login_data
            )

            if "login" not in login_resp.url and "setup" not in login_resp.url:
                successful_login = True
                break
            else:
                pass

        if not successful_login:
            pytest.skip(
                "Cannot authenticate with test CTFd instance - check credentials"
            )

        profile_resp = session.get(f"{CTFD_BASE_URL}/profile")
        assert profile_resp.status_code == 200, "Authentication failed - not logged in"

        cookie = session.cookies.get('session')
        assert cookie is not None, "No session cookie found after login"

        sio = socketio.Client()
        connected = []

        @sio.event
        def connect():
            connected.append(True)

        sio.connect(
            CTFD_BASE_URL,
            headers = {'Cookie': f'session={cookie}'}
        )

        time.sleep(2)
        assert len(connected) > 0
        sio.disconnect()
