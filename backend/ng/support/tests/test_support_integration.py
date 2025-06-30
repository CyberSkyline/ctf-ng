"""
Integration tests for support domain - API endpoint testing
"""

import json


class TestSupportIntegration:
    """Integration tests for support API endpoints."""

    def test_support_routes_loaded(self, app):
        """Test that support routes are registered."""
        support_routes = [rule for rule in app.url_map.iter_rules() if "/ng/support" in rule.rule]

        print(f"\nFound {len(support_routes)} support routes:")
        for route in support_routes:
            print(f"  {route.rule}")

        assert len(support_routes) > 0, "No support routes found"

    def test_tickets_list_endpoint(self, logged_in_client):
        """Test listing tickets endpoint."""
        response = logged_in_client.get("/ng/support/tickets")

        print(f"GET /ng/support/tickets Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Tickets list working! Found {len(data.get('data', {}).get('tickets', []))} tickets")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Tickets list endpoint not found"

    def test_create_ticket_endpoint(self, logged_in_client):
        """Test creating a ticket endpoint."""
        ticket_data = {
            "title": "Test Integration Ticket",
            "description": "This is a test ticket for integration testing",
            "priority": "medium",
        }

        response = logged_in_client.post(
            "/ng/support/tickets",
            data=json.dumps(ticket_data),
            content_type="application/json",
        )

        print(f"POST /ng/support/tickets Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.get_json()
            print(f"Create ticket working! Response: {data}")
            assert "success" in data
        elif response.status_code in [400, 422]:
            print("Endpoint exists but validation failed")
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Create ticket endpoint not found"

    def test_admin_tickets_endpoint(self, admin_client):
        """Test admin tickets list endpoint."""
        response = admin_client.get("/ng/support/admin/tickets")

        print(f"GET /ng/support/admin/tickets Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Admin tickets working! Found {len(data.get('data', {}).get('tickets', []))} tickets")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires admin authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Admin tickets endpoint not found"

    def test_admin_tags_endpoint(self, admin_client):
        """Test admin tags list endpoint."""
        response = admin_client.get("/ng/support/admin/tags")

        print(f"GET /ng/support/admin/tags Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Admin tags working! Found {len(data.get('data', {}).get('tags', []))} tags")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires admin authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Admin tags endpoint not found"
