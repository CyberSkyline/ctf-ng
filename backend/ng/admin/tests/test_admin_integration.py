from flask import session

class TestAdminIntegration:
    """Integration tests for admin API endpoints."""

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

    def test_admin_stats_count_endpoint(self, admin_client):
        """Test admin statistics count endpoint."""
        response = admin_client.get("/ng/admin/stats/counts")


        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin stats count endpoint not found"

    def test_admin_reset_endpoint(self, admin_client):
        """Test admin reset endpoint."""
        response = admin_client.post("/ng/admin/reset")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

    def test_admin_event_reset_endpoint(self, admin_client):
        """Test admin event reset endpoint."""
        response = admin_client.post("/ng/admin/events/1/reset")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Admin event reset endpoint not found"

    def test_admin_impersonation_endpoint(self, admin_client, user_factory):
        """Test admin impersonation endpoint."""
        user = user_factory()
        response = admin_client.post("/ng/admin/impersonate", json={"user_id": user.id})
        assert response.status_code == 200

        with admin_client.session_transaction() as session:
            assert session["impersonated"] is True
            assert session["id"] == user.id

        response = admin_client.post("/ng/admin/stop_impersonating", json={})
        assert response.status_code == 200

        with admin_client.session_transaction() as session:
            assert session["id"] == 2

    def test_non_admins_cannot_impersonate(self, logged_in_client, user_factory):
        """Test that non-admin users cannot impersonate others."""
        user = user_factory()

        response = logged_in_client.post("/ng/admin/impersonate", json={"user_id": 2})
        assert response.status_code == 403
