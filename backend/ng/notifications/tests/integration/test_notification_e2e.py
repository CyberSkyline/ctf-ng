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
        Test user login flow with admin created by setup script
        """
        session = requests.Session()

        # First, get the CSRF token from the homepage
        home_response = session.get(f"{CTFD_BASE_URL}/")
        csrf_token = None
        csrf_match = re.search(r"csrfToken:\s*'([^']+)'", home_response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)

        headers = {}
        if csrf_token:
            headers["CSRF-Token"] = csrf_token

        login_response = session.post(
            f"{CTFD_BASE_URL}/ng/users/login",
            headers = headers,
            json = {
                "username": "admin@examplectf.com",
                "password": "ctfng_password"
            }
        )

        assert login_response.status_code == 200, f"Login failed: {login_response.status_code} - {login_response.text}"
        assert session.cookies.get('session') is not None

    def test_websocket_with_auth(self):
        """
        Test WebSocket connection with authentication
        """
        session = requests.Session()

        # First, get the CSRF token from the homepage
        home_response = session.get(f"{CTFD_BASE_URL}/")
        csrf_token = None
        csrf_match = re.search(r"csrfToken:\s*'([^']+)'", home_response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)

        headers = {}
        if csrf_token:
            headers["CSRF-Token"] = csrf_token

        login_response = session.post(
            f"{CTFD_BASE_URL}/ng/users/login",
            headers = headers,
            json = {
                "username": "admin@examplectf.com",
                "password": "ctfng_password"
            }
        )

        if login_response.status_code != 200:
            pytest.skip(
                f"Cannot authenticate with test CTFd instance - login failed with {login_response.status_code}"
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
