"""
Integration tests for team domain - API endpoint testing
These act as quick api unit tests -
for comprehensive api tests, register as admin
and go to localhost/test-harness
"""

import json


class TestTeamIntegration:
    """Integration tests for team API endpoints."""

    def test_team_routes_loaded(self, app):
        """Test that team routes are registered."""
        team_routes = [rule for rule in app.url_map.iter_rules() if "/ng/teams" in rule.rule]

        assert len(team_routes) > 0, "No team routes found"

    def test_list_teams_endpoint(self, admin_client):
        """Test listing all teams endpoint."""
        response = admin_client.get("/ng/teams")

        assert response.status_code != 404, "Teams list endpoint not found"

    def test_team_join_endpoint(self, logged_in_client):
        """Test team join endpoint."""
        join_data = {"invite_code": "TESTCODE123"}

        response = logged_in_client.post(
            "/ng/teams/join",
            data=json.dumps(join_data),
            content_type="application/json",
        )

        assert response.status_code != 404, "Team join endpoint not found"

    def test_team_leave_endpoint(self, logged_in_client):
        """Test team leave endpoint."""
        leave_data = {"event_id": 1}

        response = logged_in_client.post(
            "/ng/teams/leave",
            data=json.dumps(leave_data),
            content_type="application/json",
        )

        assert response.status_code != 404, "Team leave endpoint not found"
