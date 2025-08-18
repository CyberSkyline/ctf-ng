from flask import session

class TestAdminIntegration:
    """Integration tests for admin API endpoints."""

    def test_admin_health_endpoint(self, admin_client):
        """Test admin health check endpoint."""
        response = admin_client.get("/ng/admin/health")

        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data

        assert response.status_code != 404, "Admin health endpoint not found"

    def test_admin_stats_endpoint(self, admin_client):
        """Test admin statistics endpoint."""
        response = admin_client.get("/ng/admin/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data

        assert response.status_code != 404, "Admin stats endpoint not found"

    def test_admin_stats_count_endpoint(self, admin_client):
        """Test admin statistics count endpoint."""
        response = admin_client.get("/ng/admin/stats/counts")


        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data

        assert response.status_code != 404, "Admin stats count endpoint not found"

    def test_admin_event_reset_endpoint(self, admin_client, event_factory):
        """Test admin event reset endpoint."""
        event = event_factory()
        response = admin_client.post(f"/ng/admin/events/{event.id}/reset", json={})

        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data

        assert response.status_code != 404, "Admin event reset endpoint not found"

class TestAdminImpersonation:

    def impersonate(self, admin_client, user_id):
        response = admin_client.post("/ng/admin/impersonate", json={"user_id": user_id})
        return response

    def stop_impersonating(self, admin_client):
        response = admin_client.post("/ng/admin/stop_impersonating", json={})
        return response

    def test_admin_impersonation_endpoint(self, admin_client, user_factory):
        """Test admin impersonation endpoint."""
        user = user_factory()
        response = self.impersonate(admin_client, user.id)
        assert response.status_code == 200

        with admin_client.session_transaction() as session:
            assert session["impersonated"] is True
            assert session["id"] == user.id

        response = self.stop_impersonating(admin_client)
        assert response.status_code == 200

        with admin_client.session_transaction() as session:
            assert session["id"] == 2

    def test_admin_identity_endpoints_report_as_user(self, admin_client, user_factory, team_factory):
        """Test that admin can perform actions as the impersonated user."""
        user = user_factory()
        team = team_factory(members=[user])
        response = self.impersonate(admin_client, user.id)
        assert response.status_code == 200

        response = admin_client.get("/ng/users/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] == user.id
        assert data["data"]["name"] == user.ctfd_user.name

        response = admin_client.get(f"/ng/users/me/teams")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"][0]["id"] == team.id

        response = self.stop_impersonating(admin_client)
        assert response.status_code == 200

        response = admin_client.get("/ng/users/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] != user.id
        assert data["data"]["name"] != user.ctfd_user.name

        response = admin_client.get(f"/ng/users/me/teams")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []

    def test_admin_team_management_as_user(self, admin_client, user_factory, team_factory, event_factory):
        user = user_factory()
        event = event_factory()

        response = self.impersonate(admin_client, user.id)
        assert response.status_code == 200

        response = admin_client.post(f"/ng/events/{event.id}/me/register", json={"team_name": "New Team"})
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["name"] == "New Team"

        response = admin_client.put(f"/ng/events/{event.id}/me/team/update_name", json={"name": "New Team Name"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["name"] == "New Team Name"

        response = admin_client.post(f"/ng/events/{event.id}/me/team/leave", json={})
        assert response.status_code == 200

        response = admin_client.get(f"/ng/users/me/teams")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []

        response = self.stop_impersonating(admin_client)
        assert response.status_code == 200

        response = admin_client.put(f"/ng/events/{event.id}/me/team/update_name", json={"name": "Newer Team name"})
        assert response.status_code == 404

    def test_admin_cannot_chain_impersonations(self, admin_client, user_factory):
        """Test that admin cannot chain impersonations."""
        user1 = user_factory(name="User 1", email="user1@example.com")
        user2 = user_factory(name="User 2", email="user2@example.com")
        response = self.impersonate(admin_client, user1.id)
        assert response.status_code == 200

        response = self.impersonate(admin_client, user2.id)
        assert response.status_code == 403

    def test_multiple_impersonations_behave_correctly(self, admin_client, user_factory):
        user1 = user_factory(name="User 1", email="user1@example.com")
        user2 = user_factory(name="User 2", email="user2@example.com")
        response = self.impersonate(admin_client, user1.id)
        assert response.status_code == 200

        response = self.stop_impersonating(admin_client)
        assert response.status_code == 200

        response = self.impersonate(admin_client, user2.id)
        assert response.status_code == 200

        response = admin_client.get("/ng/users/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] == user2.id
        assert data["data"]["name"] == user2.ctfd_user.name

    def test_impersonation_assumes_user_privileges(self, admin_client, user_factory):
        user = user_factory()

        response = admin_client.get("ng/admin/health")
        assert response.status_code == 200
        response = self.impersonate(admin_client, user.id)
        assert response.status_code == 200

        response = admin_client.get("/ng/admin/health")
        print(response.get_json())
        assert response.status_code == 403

    def test_non_admins_cannot_impersonate(self, logged_in_client, user_factory):
        """Test that non-admin users cannot impersonate others."""
        user = user_factory()

        response = logged_in_client.post("/ng/admin/impersonate", json={"user_id": 2})
        assert response.status_code == 403
