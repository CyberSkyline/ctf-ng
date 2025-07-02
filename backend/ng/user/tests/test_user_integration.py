"""
Integration tests for user domain - API endpoint testing
These act as quick api unit tests -
for comprehensive api tests, register as admin
and go to localhost/test-harness
"""


class TestUserIntegration:
    """Integration tests for user API endpoints."""

    def test_user_routes_loaded(self, app):
        """Test that user routes are registered."""
        user_routes = [rule for rule in app.url_map.iter_rules() if "/ng/users" in rule.rule]

        assert len(user_routes) > 0, "No user routes found"

    def test_list_users_endpoint(self, admin_client):
        """Test listing all users endpoint."""
        response = admin_client.get("/ng/users/all")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "Users list endpoint not found"

    def test_user_me_stats_endpoint(self, logged_in_client):
        """Test user's own stats endpoint."""
        response = logged_in_client.get("/ng/users/me/stats")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "User stats endpoint not found"

    def test_user_me_teams_endpoint(self, logged_in_client):
        """Test user's own teams endpoint."""
        response = logged_in_client.get("/ng/users/me/teams")

        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data

        assert response.status_code != 404, "User teams endpoint not found"
