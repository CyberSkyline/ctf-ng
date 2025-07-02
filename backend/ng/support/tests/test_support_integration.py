"""
Integration tests for support domain - API endpoint testing
These act as quick api unit tests -
for comprehensive api tests, register as admin
and go to localhost/test-harness
"""

import json


class TestSupportIntegration:
    """Integration tests for support API endpoints."""

    def test_support_routes_loaded(self, app):
        """Test that support routes are registered."""
        support_routes = [rule for rule in app.url_map.iter_rules() if "/ng/support" in rule.rule]

        assert len(support_routes) > 0, "No support routes found"

    def test_tickets_list_endpoint(self, logged_in_client):
        """Test listing tickets endpoint."""
        response = logged_in_client.get("/ng/support/tickets")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

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

        assert response.status_code != 404, "Create ticket endpoint not found"

    def test_admin_tickets_endpoint(self, admin_client):
        """Test admin tickets list endpoint."""
        response = admin_client.get("/ng/support/admin/tickets")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin tickets endpoint not found"

    def test_admin_tags_endpoint(self, admin_client):
        """Test admin tags list endpoint."""
        response = admin_client.get("/ng/support/admin/tags")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin tags endpoint not found"
