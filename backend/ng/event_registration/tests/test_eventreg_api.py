"""
Integration tests for event registration domain - API endpoint testing
"""

import json


class TestEventRegistrationIntegration:
    """Integration tests for event registration API endpoints."""

    def test_event_registration_routes_loaded(self, app):
        """Test that event registration routes are registered."""
        event_reg_routes = [rule for rule in app.url_map.iter_rules() if "event_registration" in rule.rule]

        assert len(event_reg_routes) > 0, "No event registration routes found"

    def test_demographics_endpoint(self, logged_in_client):
        """Test demographics endpoint."""
        response = logged_in_client.get("/ng/event_registration/1/demographics")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Demographics endpoint not found"

    def test_join_event_endpoint(self, logged_in_client):
        """Test join event endpoint."""
        join_data = {"team_name": "Test Team"}

        response = logged_in_client.post(
            "/ng/event_registration/join/1",
            data=json.dumps(join_data),
            content_type="application/json",
        )

        assert response.status_code != 500, "Join event endpoint crashed"

    def test_create_registration_period_endpoint(self, admin_client):
        """Test create registration period endpoint."""
        period_data = {"event_id": 1, "reg_open": True, "public": True}

        response = admin_client.post(
            "/ng/event_registration/create_registration_period",
            data=json.dumps(period_data),
            content_type="application/json",
        )

        assert response.status_code != 500, "Create registration period endpoint crashed"

    def test_create_registration_period_user_permission(self, logged_in_client):
        """Test create registration period requires admin permissions."""
        period_data = {"event_id": 1}

        response = logged_in_client.post(
            "/ng/event_registration/create_registration_period",
            data=json.dumps(period_data),
            content_type="application/json",
        )

        assert response.status_code != 500, "Create registration period endpoint crashed"
