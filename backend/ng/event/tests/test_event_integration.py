"""
Simple integration test for event domain - API endpoint testing
These act as quick api unit tests -
for comprehensive api tests, register as admin
and go to localhost/test-harness
"""

import json


class TestEventIntegration:
    """Integration tests for event API endpoints."""

    def test_plugin_routes_loaded(self, app):
        """Test that plugin routes are loaded."""
        ng_routes = [rule for rule in app.url_map.iter_rules() if rule.rule.startswith("/ng")]

        assert len(ng_routes) > 0, "No /ng routes found - plugin blueprints not loaded"

    def test_list_events_endpoint(self, admin_client):
        """Test listing events through the API endpoint."""
        response = admin_client.get("/ng/events")

        assert response.status_code != 404, "Events endpoint not found"

    def test_create_event_endpoint(self, admin_client):
        """Test creating an event through the API endpoint."""
        event_data = {
            "name": "Test Integration Event",
            "description": "A simple integration test event",
            "max_team_size": 4,
            "locked": False,
        }

        response = admin_client.post("/ng/events", data=json.dumps(event_data), content_type="application/json")

        assert response.status_code != 404, "Create event endpoint not found"

    def test_teams_endpoint(self, admin_client):
        """Test teams endpoint is accessible."""
        response = admin_client.get("/ng/teams")

        assert response.status_code != 404, "Teams endpoint not found"
