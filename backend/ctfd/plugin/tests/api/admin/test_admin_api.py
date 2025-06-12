"""
/plugin/tests/api/test_admin_api.py
API Tests for admin endpoints
"""

import pytest

pytestmark = pytest.mark.db


def test_admin_endpoints_require_admin(logged_in_client):
    """Check that admin endpoints require admin authentication."""
    response = logged_in_client.get("/plugin/api/admin/stats/counts")
    # CTFd's @admins_only decorator redirects non-admin users instead of returning 403
    assert response.status_code == 302
    # 302 responses don't have JSON content, they have location headers
    assert response.location is not None


def test_admin_endpoint_with_admin_user(admin_client):
    """Check that admin endpoints work for admin users."""
    response = admin_client.get("/plugin/api/admin/stats/counts")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]

    # Check that stats contain expected keys
    counts = data["data"]
    assert "events" in counts
    assert "teams" in counts
    assert "users" in counts
    assert "team_members" in counts
