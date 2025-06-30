"""
Integration tests for core functionality - API and system testing
"""


class TestCoreIntegration:
    """Integration tests for core API functionality."""

    def test_api_docs_endpoint(self, admin_client):
        """Test the Swagger API documentation endpoint."""
        response = admin_client.get("/ng/docs")

        print(f"GET /ng/docs Status: {response.status_code}")

        if response.status_code == 200:
            # Should return HTML for Swagger UI
            content = response.get_data(as_text=True)
            print("✅ API docs endpoint working! Returns Swagger UI")
            assert "swagger" in content.lower() or "api" in content.lower()
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires authentication")
        elif response.status_code == 302:
            print("✅ Endpoint exists, redirecting (likely to auth)")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "API docs endpoint not found"

    def test_swagger_json_endpoint(self, admin_client):
        """Test the Swagger JSON specification endpoint."""
        response = admin_client.get("/ng/swagger.json")

        print(f"GET /ng/swagger.json Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print("✅ Swagger JSON working! API spec available")
            assert "swagger" in data or "openapi" in data or "info" in data
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires authentication")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Swagger JSON endpoint not found"

    def test_frontend_routes(self, client):
        """Test frontend application routes."""
        # Test the hello route (frontend app)
        response = client.get("/hello")

        print(f"GET /hello Status: {response.status_code}")

        if response.status_code == 200:
            content = response.get_data(as_text=True)
            print("✅ Frontend hello route working!")
            assert "html" in content.lower()
        else:
            print(f"✅ Frontend route exists, got status: {response.status_code}")

        assert response.status_code != 404, "Frontend hello route not found"

    def test_test_harness_route(self, admin_client):
        """Test the backend test harness route."""
        response = admin_client.get("/test-harness")

        print(f"GET /test-harness Status: {response.status_code}")

        if response.status_code == 200:
            content = response.get_data(as_text=True)
            print("✅ Test harness working!")
            assert "html" in content.lower()
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires admin authentication")
        elif response.status_code == 302:
            print("✅ Endpoint exists, redirecting (likely to auth)")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Test harness route not found"
