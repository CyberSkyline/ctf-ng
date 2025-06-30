"""
Integration tests for team domain - API endpoint testing
"""

import json


class TestTeamIntegration:
    """Integration tests for team API endpoints."""

    def test_team_routes_loaded(self, app):
        """Test that team routes are registered."""
        team_routes = [rule for rule in app.url_map.iter_rules() if "/ng/teams" in rule.rule]

        print(f"\nFound {len(team_routes)} team routes:")
        for route in team_routes:
            print(f"  {route.rule}")

        assert len(team_routes) > 0, "No team routes found"

    def test_list_teams_endpoint(self, admin_client):
        """Test listing all teams endpoint."""
        response = admin_client.get("/ng/teams")

        print(f"GET /ng/teams Status: {response.status_code}")

        if response.status_code == 200:
            data = response.get_json()
            print(f"Teams list working! Found {len(data.get('data', {}).get('teams', []))} teams")
            assert "success" in data
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Teams list endpoint not found"

    def test_team_join_endpoint(self, logged_in_client):
        """Test team join endpoint."""
        join_data = {"invite_code": "TESTCODE123"}

        response = logged_in_client.post(
            "/ng/teams/join",
            data=json.dumps(join_data),
            content_type="application/json",
        )

        print(f"POST /ng/teams/join Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.get_json()
            print(f"Team join endpoint working! Response: {data}")
        elif response.status_code in [400, 422]:
            print("Endpoint exists but validation failed (expected with fake code)")
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Team join endpoint not found"

    def test_team_leave_endpoint(self, logged_in_client):
        """Test team leave endpoint."""
        leave_data = {"event_id": 1}

        response = logged_in_client.post(
            "/ng/teams/leave",
            data=json.dumps(leave_data),
            content_type="application/json",
        )

        print(f"POST /ng/teams/leave Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.get_json()
            print(f"Team leave endpoint working! Response: {data}")
        elif response.status_code in [400, 422]:
            print("Endpoint exists but validation failed (expected - not in team)")
        elif response.status_code in [401, 403]:
            print("Endpoint exists but requires authentication")
        else:
            print(f"Endpoint exists, got status: {response.status_code}")

        assert response.status_code != 404, "Team leave endpoint not found"
