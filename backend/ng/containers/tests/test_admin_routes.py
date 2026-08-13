"""
Tests for the containers admin routes.
"""

from .test_container_instance_model import make_blueprint, make_instance


def test_deployment_detail_found(admin_client, db_session, challenge, team_factory, user_factory):
    """Test that DeploymentDetail resolves the deployment for any member instance id."""
    team = team_factory(event=challenge.event, members=[user_factory(name="U1", email="u1@example.com")])
    blueprint = make_blueprint(challenge, db_session)
    instance = make_instance(blueprint, team, db_session)

    response = admin_client.get(f"/ng/admin/container/{instance.id}")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["team_name"] == team.name
    assert data["challenge_name"] == challenge.name


def test_deployment_detail_not_found(admin_client):
    """Test that DeploymentDetail 404s for an unknown instance id."""
    response = admin_client.get("/ng/admin/container/999999")

    assert response.status_code == 404
