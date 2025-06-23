"""
/backend/ctfd/plugin/tests/api/middleware/test_middleware_decorators.py
Tests for middleware decorators in the CTFd plugin.
"""

import pytest

pytestmark = pytest.mark.db

def test_lookup_by_id(temp_routes_client):
    """
    Test the user lookup middleware decorator by ID.
    """
    response = temp_routes_client.get("/test/middleware/id", query_string={"user_id": 1, "event_id": 1, "team_id": 1})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["user_id"] == 1
    assert data["event_name"] == "Temp Event"
    assert data["team_name"] == "Temp Team"

def test_lookup_by_name(temp_routes_client):
    """
    Test the team and event lookup middleware decorators by name.
    """
    response = temp_routes_client.get("/test/middleware/name", query_string={"event_name": "Temp Event"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["event_name"] == "Temp Event"

def test_multi_attribute_lookup(temp_routes_client):
    """
    Test the multi-attribute lookup middleware decorator.
    """
    response = temp_routes_client.get("/test/middleware/multi", query_string={"event_id": 1, "user_id": 1})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["team_id"] == 1

def test_relationship_lookup(temp_routes_client):
    """
    Test the relationship lookup middleware decorator.

    """
    response = temp_routes_client.get("/test/middleware/rel", query_string={"event_id": 1, "user_id": 2})
    assert response.status_code == 200
    data = response.get_json()
    print(data)
    assert data["success"] is True
    assert data["team_name"] == "Second Team"

def test_relationship_lookup_with_generic_params(temp_routes_client):
    """
    Test the relationship lookup middleware decorator with generic parameters.
    This is a more complex test to ensure the decorator can handle various types of lookups.
    """
    response = temp_routes_client.get("/test/middleware/relgen", query_string={"locked": False, "team_id": "2"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["event_name"] == "Temp Event"
    assert data["locked"] is False

def test_date_lookup(temp_routes_client):
    """
    Test the date lookup middleware decorator.
    This checks if the decorator can handle date-based lookups correctly.
    """
    response = temp_routes_client.get("/test/middleware/date", query_string={"start_time": "2023-01-01", "end_time": "2023-12-31"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["event_name"] == "Second Temp Event"

def test_lookup_missing_params(temp_routes_client):
    """
    Test the lookup middleware decorator with invalid parameters.
    This should return an error response indicating the invalid parameters.
    """
    response = temp_routes_client.get("/test/middleware/id", query_string={"invalid_param": "value"})
    assert response.status_code == 400
    data = response.get_json()
    print(data)
    assert data["success"] is False
    assert "missing_parameter" in data["errors"]

