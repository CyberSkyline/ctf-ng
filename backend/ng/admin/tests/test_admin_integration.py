"""
Integration tests for admin domain - API endpoint testing
These act as quick api unit tests -
for comprehensive api tests, register as admin
and go to localhost/test-harness
"""


class TestAdminIntegration:
    """Integration tests for admin API endpoints."""

    def test_admin_routes_loaded(self, app):
        """Test that admin routes are registered."""
        admin_routes = [rule for rule in app.url_map.iter_rules() if "/ng/admin" in rule.rule]

        assert len(admin_routes) > 0, "No admin routes found"

    def test_admin_health_endpoint(self, admin_client):
        """Test admin health check endpoint."""
        response = admin_client.get("/ng/admin/health")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin health endpoint not found"

    def test_admin_stats_endpoint(self, admin_client):
        """Test admin statistics endpoint."""
        response = admin_client.get("/ng/admin/stats")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin stats endpoint not found"
