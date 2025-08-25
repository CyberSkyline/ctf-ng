"""
Tests for the users by roles filtering endpoints
"""

import pytest
from CTFd.models import Users

from ...core.exceptions import ValidationError

from ..models.Role import Role
from ..models.enums import RoleEnum
from ...user.models.User import User as NgUser

from ..controllers.get_users_by_roles import get_users_with_roles
from ..controllers.assign_role_to_user import assign_role_to_user
from ..controllers.get_users_by_roles import get_assignable_users


pytestmark = pytest.mark.db


class TestUsersByRolesHappyPaths:
    """
    Test the flexible users by roles endpoint
    """
    @pytest.fixture
    def users_with_different_roles(self, db_session):
        """
        Create users with different role combinations
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        admin_user = Users(name = "Admin User", email = "admin@test.com")
        support_user = Users(name = "Support User", email = "support@test.com")
        both_user = Users(name = "Admin+Support User", email = "both@test.com")
        regular_user = Users(name = "Regular User", email = "regular@test.com")

        db_session.add_all([admin_user, support_user, both_user, regular_user])
        db_session.commit()

        ng_admin = NgUser.create_user(admin_user.id, commit = False)
        ng_support = NgUser.create_user(support_user.id, commit = False)
        ng_both = NgUser.create_user(both_user.id, commit = False)
        ng_regular = NgUser.create_user(regular_user.id, commit = False)

        db_session.add_all([ng_admin, ng_support, ng_both, ng_regular])
        db_session.commit()

        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)
        assign_role_to_user(support_user.id, RoleEnum.SUPPORT)
        assign_role_to_user(both_user.id, RoleEnum.ADMIN)
        assign_role_to_user(both_user.id, RoleEnum.SUPPORT)

        return {
                "admin": ng_admin,
                "support": ng_support,
                "both": ng_both,
                "regular": ng_regular,
                }

    def test_get_users_by_single_role_admin(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test getting users with only admin role
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}

        assert users_with_different_roles["admin"].id in user_ids
        assert users_with_different_roles["both"].id in user_ids
        assert users_with_different_roles["support"].id not in user_ids
        assert users_with_different_roles["regular"].id not in user_ids

    def test_get_users_by_single_role_support(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test getting users with only support role
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=support"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert users_with_different_roles["support"].id in user_ids
        assert users_with_different_roles["both"].id in user_ids
        assert users_with_different_roles["admin"].id not in user_ids
        assert users_with_different_roles["regular"].id not in user_ids

    def test_get_users_by_multiple_roles(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test getting users with multiple roles
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,support"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert users_with_different_roles["admin"].id in user_ids
        assert users_with_different_roles["support"].id in user_ids
        assert users_with_different_roles["both"].id in user_ids
        assert users_with_different_roles["regular"].id not in user_ids

    def test_get_users_by_roles_case_insensitive(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test that role names are case insensitive
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=ADMIN,Support"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert users_with_different_roles["admin"].id in user_ids
        assert users_with_different_roles["support"].id in user_ids
        assert users_with_different_roles["both"].id in user_ids

    def test_get_users_by_roles_with_spaces(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test that extra spaces are handled properly
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles= admin , support "
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert users_with_different_roles["admin"].id in user_ids
        assert users_with_different_roles["support"].id in user_ids

    def test_get_users_invalid_role(self, admin_client):
        """
        Test error when providing invalid role names
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=invalid_role"
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "validation" in data["errors"]
        assert "admin" in data["errors"]["validation"]
        assert "support" in data["errors"]["validation"]

    def test_get_users_mixed_valid_invalid_roles(self, admin_client):
        """
        Test error when mixing valid and invalid role names
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,superhero,support"
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "superhero" in data["errors"]["validation"]

    def test_get_users_no_roles_specified(self, admin_client):
        """
        Test error when no roles query parameter provided
        """
        response = admin_client.get("/ng/admin/permissions/users_by_roles")

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "specify roles" in data["errors"]["validation"].lower()

    def test_get_users_empty_roles_parameter(self, admin_client):
        """
        Test error when roles parameter is empty
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles="
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_get_users_only_commas(self, admin_client):
        """
        Test error when roles parameter contains only commas/spaces
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles= , , "
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_non_admin_cannot_access(self, logged_in_client):
        """
        Test that non-admins cannot access the endpoint
        """
        response = logged_in_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )
        assert response.status_code in [302, 403]

    def test_unauthenticated_cannot_access(self, client):
        """
        Test that unauthenticated users cannot access the endpoint
        """
        response = client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )
        assert response.status_code in [302, 403, 401]

    def test_response_includes_user_roles(
            self,
            admin_client,
            users_with_different_roles
            ):
        """
        Test that response includes user role information for admin requests
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,support"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        both_user_data = None
        for user in data["data"]:
            if user["id"] == users_with_different_roles["both"].id:
                both_user_data = user
                break

        assert both_user_data is not None
        assert "roles" in both_user_data
        assert "admin" in both_user_data["roles"]
        assert "support" in both_user_data["roles"]

    def test_empty_result_for_roles_with_no_users(
            self,
            admin_client,
            db_session
            ):
        """
        Test that empty list is returned when no users have the requested roles
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


class TestAssignableUsersHappyPaths:
    """
    Test the convenience endpoint for getting assignable users
    """
    @pytest.fixture
    def mixed_role_users(self, db_session):
        """
        Create users with admin/support roles and some without for testing assignable endpoint
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        admin_user = Users(name = "Admin User", email = "admin_assign@test.com")
        support_user = Users(
                name = "Support User",
                email = "support_assign@test.com"
                )
        regular_user = Users(
                name = "Regular User",
                email = "regular_assign@test.com"
                )

        db_session.add_all([admin_user, support_user, regular_user])
        db_session.commit()

        ng_admin = NgUser.create_user(admin_user.id, commit = False)
        ng_support = NgUser.create_user(support_user.id, commit = False)
        ng_regular = NgUser.create_user(regular_user.id, commit = False)

        db_session.add_all([ng_admin, ng_support, ng_regular])
        db_session.commit()

        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)
        assign_role_to_user(support_user.id, RoleEnum.SUPPORT)

        return {
                "admin": ng_admin,
                "support": ng_support,
                "regular": ng_regular,
                }

    def test_get_assignable_users(self, admin_client, mixed_role_users):
        """
        Test getting users who can be assigned to tickets (admin + support roles)
        """
        response = admin_client.get("/ng/admin/permissions/tickets/assignable_users")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert mixed_role_users["admin"].id in user_ids
        assert mixed_role_users["support"].id in user_ids

        assert mixed_role_users["regular"].id not in user_ids

    def test_assignable_users_includes_role_info(
            self,
            admin_client,
            mixed_role_users
            ):
        """
        Test that assignable users endpoint includes role information
        """
        response = admin_client.get("/ng/admin/permissions/tickets/assignable_users")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        admin_user_data = None
        for user in data["data"]:
            if user["id"] == mixed_role_users["admin"].id:
                admin_user_data = user
                break

        assert admin_user_data is not None
        assert "roles" in admin_user_data
        assert "admin" in admin_user_data["roles"]

    def test_assignable_users_non_admin_cannot_access(self, logged_in_client):
        """
        Test that non admins cannot access assignable users endpoint
        """
        response = logged_in_client.get(
                "/ng/admin/permissions/tickets/assignable_users"
                )
        assert response.status_code in [302, 403]

    def test_assignable_users_unauthenticated_cannot_access(self, client):
        """
        Test that unauthenticated users cannot access assignable users endpoint
        """
        response = client.get("/ng/admin/permissions/tickets/assignable_users")
        assert response.status_code in [302, 403, 401]


class TestSupportTicketAssignmentIntegration:
    """
    Integration testing how it may work with support ticket assignment
    """
    @pytest.fixture
    def ticket_assignment_scenario(
            self,
            db_session,
            event_factory,
            ticket_factory
            ):
        """
        Create a realistic ticket assignment scenario
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        admin_user = Users(
                name = "Ticket Admin",
                email = "ticket_admin@test.com",
                type = "admin"
                )
        support_user = Users(
                name = "Support Staff",
                email = "support_staff@test.com"
                )
        regular_user = Users(
                name = "Ticket Creator",
                email = "ticket_creator@test.com"
                )

        db_session.add_all([admin_user, support_user, regular_user])
        db_session.commit()

        ng_admin = NgUser.create_user(admin_user.id, commit = False)
        ng_support = NgUser.create_user(support_user.id, commit = False)
        ng_regular = NgUser.create_user(regular_user.id, commit = False)

        db_session.add_all([ng_admin, ng_support, ng_regular])
        db_session.commit()

        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)
        assign_role_to_user(support_user.id, RoleEnum.SUPPORT)

        event = event_factory()
        ticket = ticket_factory(
                subject = "Need help with challenge",
                author_id = regular_user.id,
                event_id = event.id
                )

        return {
                "admin_user": ng_admin,
                "support_user": ng_support,
                "regular_user": ng_regular,
                "ticket": ticket,
                "ctfd_admin": admin_user,
                }

    def test_full_ticket_assignment_workflow(
            self,
            app,
            db_session,
            ticket_assignment_scenario
            ):
        """
        Test the complete workflow: get assignable users → assign ticket
        """
        scenario = ticket_assignment_scenario

        admin_client = app.test_client()
        with admin_client.session_transaction() as sess:
            sess["id"] = scenario["ctfd_admin"].id
            sess["name"] = scenario["ctfd_admin"].name
            sess["type"] = scenario["ctfd_admin"].type
            sess["nonce"] = "test-nonce"

        response = admin_client.get("/ng/admin/permissions/tickets/assignable_users")
        assert response.status_code == 200

        data = response.get_json()
        assignable_users = data["data"]

        assignable_ids = {u["id"] for u in assignable_users}
        assert scenario["admin_user"].id in assignable_ids
        assert scenario["support_user"].id in assignable_ids
        assert scenario["regular_user"].id not in assignable_ids

        ticket_id = scenario["ticket"].id
        support_user_id = scenario["support_user"].id

        response = admin_client.put(
                f"/ng/admin/support/tickets/{ticket_id}/assign",
                json = {"user_id": support_user_id}
                )
        assert response.status_code == 200

        assign_data = response.get_json()
        assert assign_data["success"] is True
        assert assign_data["data"]["assigned_to"] == support_user_id

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )
        assert response.status_code == 200

        admin_users = response.get_json()["data"]
        admin_ids = {u["id"] for u in admin_users}
        assert scenario["admin_user"].id in admin_ids
        assert scenario["support_user"].id not in admin_ids

    def test_role_based_assignment_permissions(
            self,
            admin_client,
            ticket_assignment_scenario
            ):
        """
        Test that we can filter users by role for different types of assignments
        """
        scenario = ticket_assignment_scenario

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )
        assert response.status_code == 200

        admin_only = response.get_json()["data"]
        admin_ids = {u["id"] for u in admin_only}
        assert scenario["admin_user"].id in admin_ids
        assert scenario["support_user"].id not in admin_ids

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=support"
                )
        assert response.status_code == 200

        support_only = response.get_json()["data"]
        support_ids = {u["id"] for u in support_only}
        assert scenario["support_user"].id in support_ids
        assert scenario["admin_user"].id not in support_ids

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,support"
                )
        assert response.status_code == 200

        all_assignable = response.get_json()["data"]
        all_ids = {u["id"] for u in all_assignable}
        assert scenario["admin_user"].id in all_ids
        assert scenario["support_user"].id in all_ids
        assert scenario["regular_user"].id not in all_ids


class TestControllerUnits:
    """
    Unit tests for the controller functions directly
    """
    @pytest.fixture
    def controller_test_users(self, db_session):
        """
        Create minimal users for controller testing
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        admin_ctfd = Users(
                name = "Controller Admin",
                email = "controller_admin@test.com"
                )
        support_ctfd = Users(
                name = "Controller Support",
                email = "controller_support@test.com"
                )

        db_session.add_all([admin_ctfd, support_ctfd])
        db_session.commit()

        admin_ng = NgUser.create_user(admin_ctfd.id, commit = False)
        support_ng = NgUser.create_user(support_ctfd.id, commit = False)

        db_session.add_all([admin_ng, support_ng])
        db_session.commit()

        assign_role_to_user(admin_ctfd.id, RoleEnum.ADMIN)
        assign_role_to_user(support_ctfd.id, RoleEnum.SUPPORT)

        return {"admin": admin_ng, "support": support_ng}

    def test_get_users_with_roles_controller(
            self,
            db_session,
            controller_test_users
            ):
        """
        Test get_users_with_roles controller function directly
        """
        admin_users = get_users_with_roles(["admin"])
        admin_ids = {u.id for u in admin_users}
        assert controller_test_users["admin"].id in admin_ids
        assert controller_test_users["support"].id not in admin_ids

        all_users = get_users_with_roles(["admin", "support"])
        all_ids = {u.id for u in all_users}
        assert controller_test_users["admin"].id in all_ids
        assert controller_test_users["support"].id in all_ids

    def test_get_users_with_roles_invalid_role(self, controller_test_users):
        """
        Test that controller raises ValidationError for invalid roles
        """
        with pytest.raises(ValidationError) as exc_info:
            get_users_with_roles(["invalid_role"])

        error_msg = str(exc_info.value)
        assert "invalid_role" in error_msg
        assert "admin" in error_msg
        assert "support" in error_msg

    def test_get_assignable_users_controller(
            self,
            db_session,
            controller_test_users
            ):
        """
        Test get_assignable_users controller function directly
        """
        assignable = get_assignable_users()
        assignable_ids = {u.id for u in assignable}

        assert controller_test_users["admin"].id in assignable_ids
        assert controller_test_users["support"].id in assignable_ids


class TestEdgeCases:
    """
    Test edge cases
    """
    @pytest.fixture
    def basic_role_users(self, db_session):
        """
        Create minimal users for edge case testing
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        admin_user = Users(name = "Edge Admin", email = "edge_admin@test.com")
        db_session.add(admin_user)
        db_session.commit()

        ng_admin = NgUser.create_user(admin_user.id, commit = False)
        db_session.add(ng_admin)
        db_session.commit()

        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)
        return ng_admin

    def test_duplicate_roles_in_query(self, admin_client, basic_role_users):
        """
        Test handling of duplicate roles in query string
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,admin,admin,support,admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        user_ids = {u["id"] for u in data["data"]}
        assert basic_role_users.id in user_ids

    def test_extremely_long_role_string(self, admin_client, basic_role_users):
        """
        Test very long query strings
        """
        long_roles = ",".join(["admin", "support"] * 100)

        response = admin_client.get(
                f"/ng/admin/permissions/users_by_roles?roles={long_roles}"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_unicode_role_names(self, admin_client):
        """
        Test unicode in role names
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=adminé,supportñ"
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_extremely_long_single_role_name(self, admin_client):
        """
        Test single role name that's extremely long
        """
        long_role = "a" * 10000

        response = admin_client.get(
                f"/ng/admin/permissions/users_by_roles?roles={long_role}"
                )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_orphaned_role_assignments(self, admin_client, db_session):
        """
        Test users with role assignments but missing User records
        """
        Role.create_role(RoleEnum.ADMIN)

        admin_ctfd = Users(
                name = "Soon to be corrupted",
                email = "corrupt@test.com"
                )
        db_session.add(admin_ctfd)
        db_session.commit()

        ng_admin = NgUser.create_user(admin_ctfd.id, commit = False)
        db_session.add(ng_admin)
        db_session.commit()

        assign_role_to_user(admin_ctfd.id, RoleEnum.ADMIN)

        db_session.delete(admin_ctfd)
        db_session.commit()

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        # Should either exclude the corrupted user or handle it gracefully

    def test_user_with_no_ctfd_reference(self, admin_client, db_session):
        """
        Test ng_user that exists but has corrupted CTFd user reference
        """
        Role.create_role(RoleEnum.ADMIN)

        temp_user = Users(name = "Temp User", email = "temp@test.com")
        db_session.add(temp_user)
        db_session.commit()

        user_id = temp_user.id

        ng_user = NgUser(id = user_id)
        db_session.add(ng_user)
        db_session.commit()

        assign_role_to_user(user_id, RoleEnum.ADMIN)

        db_session.delete(temp_user)
        db_session.commit()

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        # Should handle gracefully
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_large_result_set_performance(self, admin_client, db_session):
        """
        Test performance with many users having same role
        """
        Role.create_role(RoleEnum.ADMIN)

        user_ids = []
        for i in range(100):
            ctfd_user = Users(
                    name = f"LoadTest{i}",
                    email = f"load{i}@test.com"
                    )
            db_session.add(ctfd_user)
            db_session.commit()

            ng_user = NgUser.create_user(ctfd_user.id, commit = False)
            db_session.add(ng_user)
            db_session.commit()

            assign_role_to_user(ctfd_user.id, RoleEnum.ADMIN)
            user_ids.append(ng_user.id)

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 100

    def test_memory_usage_with_many_roles(self, admin_client, db_session):
        """
        Test memory efficiency with role combinations
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        for i in range(10):
            ctfd_user = Users(
                    name = f"DualRole{i}",
                    email = f"dual{i}@test.com"
                    )
            db_session.add(ctfd_user)
            db_session.commit()

            ng_user = NgUser.create_user(ctfd_user.id, commit = False)
            db_session.add(ng_user)
            db_session.commit()

            assign_role_to_user(ctfd_user.id, RoleEnum.ADMIN)
            assign_role_to_user(ctfd_user.id, RoleEnum.SUPPORT)

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin,support"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        # Verify no duplicates in response (set deduplication worked)
        user_ids = [u["id"] for u in data["data"]]
        assert len(user_ids) == len(set(user_ids)), "Response should not contain duplicate users"

    def test_assignable_users_with_large_dataset(
            self,
            admin_client,
            db_session
            ):
        """
        Test assignable users endpoint with many users
        """
        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)

        assignable_count = 0
        for i in range(50):
            ctfd_user = Users(name = f"Scale{i}", email = f"scale{i}@test.com")
            db_session.add(ctfd_user)
            db_session.commit()

            ng_user = NgUser.create_user(ctfd_user.id, commit = False)
            db_session.add(ng_user)
            db_session.commit()

            if i % 3 == 0:
                assign_role_to_user(ctfd_user.id, RoleEnum.ADMIN)
                assignable_count += 1
            elif i % 5 == 0:
                assign_role_to_user(ctfd_user.id, RoleEnum.SUPPORT)
                assignable_count += 1

        response = admin_client.get("/ng/admin/permissions/tickets/assignable_users")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= assignable_count

    def test_user_creation_during_request(self, admin_client, db_session):
        """
        Test behavior when users are being created during request
        """
        Role.create_role(RoleEnum.ADMIN)

        initial_user = Users(name = "Initial", email = "initial@test.com")
        db_session.add(initial_user)
        db_session.commit()

        ng_initial = NgUser.create_user(initial_user.id, commit = False)
        db_session.add(ng_initial)
        db_session.commit()

        assign_role_to_user(initial_user.id, RoleEnum.ADMIN)

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) >= 1

    def test_role_enum_values_exist(self):
        """
        Test that required RoleEnum values exist
        """
        assert hasattr(RoleEnum, 'ADMIN')
        assert hasattr(RoleEnum, 'SUPPORT')
        assert RoleEnum.ADMIN.value == 'admin'
        assert RoleEnum.SUPPORT.value == 'support'

    def test_malformed_response_handling(self, admin_client, db_session):
        """
        Test handling of potential serialization issues
        """
        Role.create_role(RoleEnum.ADMIN)

        admin_user = Users(
                name = "Serialize Test",
                email = "serialize@test.com"
                )
        db_session.add(admin_user)
        db_session.commit()

        ng_admin = NgUser.create_user(admin_user.id, commit = False)
        db_session.add(ng_admin)
        db_session.commit()

        assign_role_to_user(admin_user.id, RoleEnum.ADMIN)

        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        assert "success" in data
        assert "data" in data

        for user in data["data"]:
            assert "id" in user
            assert "name" in user
            assert isinstance(user["id"], int)

    def test_request_size_limits(self, admin_client):
        """
        Test behavior with large request parameters
        """
        max_length_roles = "admin," * 1000

        response = admin_client.get(
                f"/ng/admin/permissions/users_by_roles?roles={max_length_roles}"
                )

        # Should either work or return proper error, not crash
        assert response.status_code in [200, 400, 414]    # 414 = URI Too Long

    def test_empty_database_state(self, admin_client, db_session):
        """
        Test behavior when database is in empty/clean state
        """
        response = admin_client.get(
                "/ng/admin/permissions/users_by_roles?roles=admin"
                )

        # Should handle empty state gracefully
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.get_json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
