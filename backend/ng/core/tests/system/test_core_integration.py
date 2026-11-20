"""
Integration tests for core functionality - API and system testing
"""


class TestCoreIntegration:
    """Integration tests for core API functionality."""

    def test_api_docs_endpoint(self, admin_client):
        """Test the Swagger API documentation endpoint."""
        response = admin_client.get("/ng/docs")

        assert response.status_code == 200
        # Should return HTML for Swagger UI
        assert "swagger" in response.get_data(as_text=True).lower()

    def test_swagger_json_endpoint(self, admin_client):
        """Test the Swagger JSON specification endpoint."""
        response = admin_client.get("/ng/swagger.json")

        assert response.status_code == 200
        data = response.get_json()
        assert "swagger" in data
        assert "paths" in data

    def test_frontend_routes(self, client):
        """Test frontend application routes."""
        # Test the root route (frontend app)
        response = client.get("/")

        assert response.status_code == 200
        assert "<html" in response.get_data(as_text=True).lower()
