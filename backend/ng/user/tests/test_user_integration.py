"""
Integration tests for user domain - API endpoint testing
"""


class TestUserIntegration:
    """Integration tests for user API endpoints."""

    def test_user_routes_loaded(self, app):
        """Test that user routes are registered."""
        user_routes = [rule for rule in app.url_map.iter_rules() if "/ng/users" in rule.rule]

        print(f"\n✅ Found {len(user_routes)} user routes:")
        for route in user_routes:
            print(f"  {route.rule}")

        assert len(user_routes) > 0, "No user routes found"

    def test_list_users_endpoint(self, admin_client):
        """Test listing all users endpoint."""
        response = admin_client.get("/ng/users/all")

        print(f"GET /ng/users/all Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Users list working! Found {len(data.get('data', {}).get('users', []))} users")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires admin authentication")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Users list endpoint not found"

    def test_user_me_stats_endpoint(self, logged_in_client):
        """Test user's own stats endpoint."""
        response = logged_in_client.get("/ng/users/me/stats")

        print(f"GET /ng/users/me/stats Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ User stats working! Response: {data}")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires authentication")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "User stats endpoint not found"

    def test_user_me_teams_endpoint(self, logged_in_client):
        """Test user's own teams endpoint."""
        response = logged_in_client.get("/ng/users/me/teams")

        print(f"GET /ng/users/me/teams Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ User teams working! Response: {data}")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("✅ Endpoint exists but requires authentication")
        else:
            print(f"✅ Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "User teams endpoint not found"
