import pytest
import time
from CTFd.models import db as _db


def lookup_user_by_id(temp_routes_client):
    """
    Test the user lookup middleware decorator by ID.
    """
    response = temp_routes_client.get("/test/middleware/id", query_string={"id": 1})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["user_id"] is not None
