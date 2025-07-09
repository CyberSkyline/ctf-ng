"""
Integration tests for core functionality - API and system testing
"""


class TestCoreIntegration:
    """Integration tests for core API functionality."""

    def test_api_docs_endpoint(self, admin_client):
        """Test the Swagger API documentation endpoint."""
        response = admin_client.get("/ng/docs")

        if response.status_code == 200:
            # Should return HTML for Swagger UI
            content = response.get_data(as_text=True)
            assert "swagger" in content.lower() or "api" in content.lower()

        assert response.status_code != 404, "API docs endpoint not found"

    def test_swagger_json_endpoint(self, admin_client):
        """Test the Swagger JSON specification endpoint."""
        response = admin_client.get("/ng/swagger.json")

        if response.status_code == 200:
            data = response.get_json()
            assert "swagger" in data or "openapi" in data or "info" in data

        assert response.status_code != 404, "Swagger JSON endpoint not found"

    def test_frontend_routes(self, client):
        """Test frontend application routes."""
        # Test the hello route (frontend app)
        response = client.get("/hello")

        if response.status_code == 200:
            content = response.get_data(as_text=True)
            assert "html" in content.lower()

        assert response.status_code != 404, "Frontend hello route not found"

    def test_test_harness_route(self, admin_client):
        """Test the backend test harness route."""
        response = admin_client.get("/test-harness")

        if response.status_code == 200:
            content = response.get_data(as_text=True)
            assert "html" in content.lower()

        assert response.status_code != 404, "Test harness route not found"
