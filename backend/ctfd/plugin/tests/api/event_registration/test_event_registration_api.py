"""
/backend/ctfd/plugin/tests/api/event_registration/__init__.py
Event Registration API endpoint tests package.
"""

import pytest
from plugin.user.models.User import User
from flask import g

pytestmark = pytest.mark.db

def test_get_user_demographics_authentication(logged_in_client,event):
    """Check that user demographics endpoint works for authenticated users."""
    g.user = User(id=1)
    response = logged_in_client.get("/plugin/api/event_registration", query_string={"event_id": event.id})
    print(response)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"]
    assert "demographics" in data["data"]
    assert isinstance(data["data"]["demographics"], list)
    assert len(data["data"]["demographics"]) > 0
    

