"""
plugin/tests/test_api.py
API Tests
"""

import pytest
import json
from CTFd.models import db
from tests.helpers import gen_user

from ..helpers import create_ctfd, destroy_ctfd, get_models


class TestAPI:

    def test_teams_endpoint_requires_authentication(self):
        """Check that teams endpoint requires authentication."""
        app = create_ctfd()

        with app.app_context():
            with app.test_client() as client:
                response = client.get("/plugin/api/teams?world_id=1")
                assert response.status_code in [302, 403]

        destroy_ctfd(app)

    def test_teams_endpoint_with_authentication(self):
        """Check that teams endpoint works with authentication."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]

            user = gen_user(db, name="testuser", email="test@example.com")

            world = World(name="Test World", description="Test Description")
            db.session.add(world)
            db.session.commit()

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.get(f"/plugin/api/teams?world_id={world.id}")
                assert response.status_code == 200

                data = response.get_json()
                assert "success" in data
                assert data["success"] == True

        destroy_ctfd(app)

    def test_worlds_endpoint_with_authentication(self):
        """Check that worlds endpoint works with authentication."""
        app = create_ctfd()

        with app.app_context():
            user = gen_user(db, name="testuser", email="test@example.com")

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.get("/plugin/api/worlds")
                assert response.status_code == 200

                data = response.get_json()
                assert "success" in data
                assert data["success"] == True

        destroy_ctfd(app)

    def test_users_me_teams_endpoint(self):
        """Check that user teams endpoint works correctly."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            User = models["User"]

            user = gen_user(db, name="testuser", email="test@example.com")

            ng_user = User(id=user.id)
            db.session.add(ng_user)
            db.session.commit()

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.get("/plugin/api/users/me/teams")
                assert response.status_code == 200

                data = response.get_json()
                assert "success" in data
                assert data["success"] == True

        destroy_ctfd(app)

    def test_admin_endpoints_require_admin(self):
        """Check that admin endpoints require admin privileges."""
        app = create_ctfd()

        with app.app_context():
            regular_user = gen_user(db, name="testuser", email="test@example.com")

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = regular_user.id
                    sess["name"] = regular_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.get("/plugin/api/admin/stats")
                assert response.status_code in [302, 403]

        destroy_ctfd(app)

    def test_admin_endpoint_with_admin_user(self):
        """Check that admin endpoints work with admin user."""
        app = create_ctfd()

        with app.app_context():
            admin_user = gen_user(db, name="admin", email="admin@example.com", type="admin")

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = admin_user.id
                    sess["name"] = admin_user.name
                    sess["type"] = "admin"
                    sess["nonce"] = "test-nonce"

                response = client.get("/plugin/api/admin/stats/counts")
                assert response.status_code == 200

                data = response.get_json()
                assert "success" in data
                assert data["success"] == True

        destroy_ctfd(app)

    def test_create_team_requires_data(self):
        """Check that team creation requires proper data."""
        app = create_ctfd()

        with app.app_context():
            user = gen_user(db, name="testuser", email="test@example.com")

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.post("/plugin/api/teams", json={})
                assert response.status_code == 400

                data = response.get_json()
                assert "success" in data
                assert data["success"] == False

        destroy_ctfd(app)

    def test_create_world_requires_admin(self):
        """Check that world creation requires admin privileges."""
        app = create_ctfd()

        with app.app_context():
            regular_user = gen_user(db, name="testuser", email="test@example.com")

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = regular_user.id
                    sess["name"] = regular_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                world_data = {
                    "name": "New World",
                    "description": "A new training world",
                }

                response = client.post("/plugin/api/worlds", json=world_data)
                assert response.status_code in [302, 403]

        destroy_ctfd(app)

    def test_api_endpoints_return_json(self):
        """Check that API endpoints return JSON responses."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]
            User = models["User"]

            user = gen_user(db, name="testuser", email="test@example.com")

            ng_user = User(id=user.id)
            db.session.add(ng_user)

            world = World(name="Test World", description="Test Description")
            db.session.add(world)
            db.session.commit()

            team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
            db.session.add(team)
            db.session.commit()

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                endpoints_to_test = [
                    f"/plugin/api/teams?world_id={world.id}",
                    "/plugin/api/worlds",
                    f"/plugin/api/worlds/{world.id}",
                    f"/plugin/api/teams/{team.id}",
                    "/plugin/api/users/me/teams",
                ]

                for endpoint in endpoints_to_test:
                    response = client.get(endpoint)
                    assert response.status_code == 200

                    data = response.get_json()
                    assert data is not None
                    assert isinstance(data, dict)
                    assert "success" in data

        destroy_ctfd(app)

    def test_captain_assignment_security(self):
        """Check that captain assignment has proper security rules."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]
            User = models["User"]
            TeamMember = models["TeamMember"]

            captain_user = gen_user(db, name="captain", email="captain@example.com")
            member_user = gen_user(db, name="member", email="member@example.com")
            other_user = gen_user(db, name="other", email="other@example.com")
            admin_user = gen_user(db, name="admin", email="admin@example.com", type="admin")

            ng_captain = User(id=captain_user.id)
            ng_member = User(id=member_user.id)
            ng_other = User(id=other_user.id)
            ng_admin = User(id=admin_user.id)
            db.session.add_all([ng_captain, ng_member, ng_other, ng_admin])

            world = World(name="Test World", description="Test Description")
            db.session.add(world)
            db.session.commit()

            team = Team(name="Test Team", world_id=world.id, limit=4, invite_code="TEST123")
            db.session.add(team)
            db.session.commit()

            captain_membership = TeamMember(
                user_id=captain_user.id,
                team_id=team.id,
                world_id=world.id,
                role="captain",
            )
            member_membership = TeamMember(
                user_id=member_user.id,
                team_id=team.id,
                world_id=world.id,
                role="member",
            )
            db.session.add_all([captain_membership, member_membership])
            db.session.commit()

            with app.test_client() as client:

                with client.session_transaction() as sess:
                    sess["id"] = member_user.id
                    sess["name"] = member_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.post(
                    f"/plugin/api/teams/{team.id}/captain",
                    json={"user_id": member_user.id},
                )
                assert response.status_code == 403
                data = response.get_json()
                assert data["success"] == False
                assert "You are not authorized to assign captain" in data["errors"]["captain"]

                with client.session_transaction() as sess:
                    sess["id"] = other_user.id
                    sess["name"] = other_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.post(
                    f"/plugin/api/teams/{team.id}/captain",
                    json={"user_id": member_user.id},
                )
                assert response.status_code == 403

                with client.session_transaction() as sess:
                    sess["id"] = captain_user.id
                    sess["name"] = captain_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.post(
                    f"/plugin/api/teams/{team.id}/captain",
                    json={"user_id": member_user.id},
                )
                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] == True
                assert data["data"]["captain_id"] == member_user.id

                updated_captain = TeamMember.query.filter_by(team_id=team.id, role="captain").first()
                assert updated_captain.user_id == member_user.id

                # Admin can assign captain even if not in team
                with client.session_transaction() as sess:
                    sess["id"] = admin_user.id
                    sess["name"] = admin_user.name
                    sess["type"] = "admin"
                    sess["nonce"] = "test-nonce"

                response = client.post(
                    f"/plugin/api/teams/{team.id}/captain",
                    json={"user_id": captain_user.id},
                )
                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] == True
                assert data["data"]["captain_id"] == captain_user.id

        destroy_ctfd(app)

    def test_create_team_creator_becomes_captain(self):
        """Check that team creator automatically becomes captain."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            User = models["User"]
            TeamMember = models["TeamMember"]

            user = gen_user(db, name="creator", email="creator@example.com")
            ng_user = User(id=user.id)
            db.session.add(ng_user)

            world = World(name="Test World", description="Test Description")
            db.session.add(world)
            db.session.commit()

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["name"] = user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                team_data = {"name": "New Team", "world_id": world.id}

                response = client.post("/plugin/api/teams", json=team_data)
                assert response.status_code == 201
                data = response.get_json()
                assert data["success"] == True
                team_id = data["data"]["team"]["id"]

                # Verify creator is captain
                captain = TeamMember.query.filter_by(team_id=team_id, role="captain").first()
                assert captain is not None
                assert captain.user_id == user.id

        destroy_ctfd(app)

    def test_update_team_endpoint(self):
        """Check that team update endpoint works correctly."""
        app = create_ctfd()

        with app.app_context():
            models = get_models()
            World = models["World"]
            Team = models["Team"]
            User = models["User"]
            TeamMember = models["TeamMember"]

            captain_user = gen_user(db, name="captain", email="captain@example.com")
            member_user = gen_user(db, name="member", email="member@example.com")

            ng_captain = User(id=captain_user.id)
            ng_member = User(id=member_user.id)
            db.session.add_all([ng_captain, ng_member])

            world = World(name="Test World", description="Test Description")
            db.session.add(world)
            db.session.commit()

            team = Team(name="Original Name", world_id=world.id, limit=4, invite_code="TEST123")
            db.session.add(team)
            db.session.commit()

            captain_membership = TeamMember(
                user_id=captain_user.id,
                team_id=team.id,
                world_id=world.id,
                role="captain",
            )
            member_membership = TeamMember(
                user_id=member_user.id,
                team_id=team.id,
                world_id=world.id,
                role="member",
            )
            db.session.add_all([captain_membership, member_membership])
            db.session.commit()

            with app.test_client() as client:

                with client.session_transaction() as sess:
                    sess["id"] = member_user.id
                    sess["name"] = member_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.patch(f"/plugin/api/teams/{team.id}", json={"name": "Hacked Name"})
                assert response.status_code == 403

                with client.session_transaction() as sess:
                    sess["id"] = captain_user.id
                    sess["name"] = captain_user.name
                    sess["type"] = "user"
                    sess["nonce"] = "test-nonce"

                response = client.patch(f"/plugin/api/teams/{team.id}", json={"name": "New Name"})
                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] == True

                updated_team = Team.query.get(team.id)
                assert updated_team.name == "New Name"

        destroy_ctfd(app)
