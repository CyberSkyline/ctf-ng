"""
Integration tests for admin domain - API endpoint testing
"""


class TestAdminIntegration:
    """Integration tests for admin API endpoints."""

    def test_admin_routes_loaded(self, app):
        """Test that admin routes are registered."""
        admin_routes = [rule for rule in app.url_map.iter_rules() if "/ng/admin" in rule.rule]

        print(f"\nFound {len(admin_routes)} admin routes:")
        for route in admin_routes:
            print(f"  {route.rule}")

        assert len(admin_routes) > 0, "No admin routes found"

    def test_admin_health_endpoint(self, admin_client):
        """Test admin health check endpoint."""
        response = admin_client.get("/ng/admin/health")

        print(f"GET /ng/admin/health Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Admin health working! Response: {data}")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires admin authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Admin health endpoint not found"

    def test_admin_stats_endpoint(self, admin_client):
        """Test admin statistics endpoint."""
        response = admin_client.get("/ng/admin/stats")

        print(f"GET /ng/admin/stats Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Admin stats working! Response: {data}")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires admin authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Admin stats endpoint not found"

    def test_admin_cleanup_endpoint(self, admin_client):
        """Test admin cleanup endpoint."""
        response = admin_client.post("/ng/admin/cleanup")

        print(f"POST /ng/admin/cleanup Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Admin cleanup working! Response: {data}")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires admin authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Admin cleanup endpoint not found"
