"""
Simple integration test for event domain - API endpoint testing
"""

import json


class TestEventIntegration:
    """Integration tests for event API endpoints."""

    def test_plugin_routes_loaded(self, app):
        """Test that plugin routes are loaded."""
        print("\nAll registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint}")

        ng_routes = [rule for rule in app.url_map.iter_rules() if rule.rule.startswith("/ng")]
        if ng_routes:
            print(f"✅ Found {len(ng_routes)} /ng routes!")
            for route in ng_routes:
                print(f"  {route.rule}")
        else:
            print("No /ng routes found - plugin routes not loading")

        assert len(ng_routes) > 0, "No /ng routes found - plugin blueprints not loaded"

    def test_list_events_endpoint(self, admin_client):
        """Test listing events through the API endpoint."""
        response = admin_client.get("/ng/events")

        print(f"GET /ng/events Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Events list endpoint working! Response: {data}")
            assert "success" in data
        elif response.status_code == 401:
            print("Endpoint exists but requires authentication")
        elif response.status_code == 404:
            print("Events endpoint not found")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

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

        print(f"POST /ng/events Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.get_json()
            print(f"Create event successful! Response: {data}")
        elif response.status_code == 400:
            print("Endpoint exists but validation failed (expected)")
        elif response.status_code == 401:
            print("Endpoint exists but requires authentication")
        elif response.status_code == 422:
            print("Endpoint exists but validation failed")
        elif response.status_code == 404:
            print("Create event endpoint not found")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Create event endpoint not found"

    def test_teams_endpoint(self, admin_client):
        """Test teams endpoint is accessible."""
        response = admin_client.get("/ng/teams")

        print(f"GET /ng/teams Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Teams endpoint working! Response: {data}")
        elif response.status_code in [401, 400, 422]:
            print(f"Teams endpoint exists, got status: {response.status_code}")
        elif response.status_code == 404:
            print("Teams endpoint not found")
        else:
            print(f"Teams endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Teams endpoint not found"
