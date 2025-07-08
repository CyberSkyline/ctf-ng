"""
Defines shared Pytest fixtures for application setup.
/backend/ng/conftest.py

Conftest.py is now located in plugin/ instead of plugin/core/testing/
because to make its fixtures, like the database session and app client,
globally available to all tests in every domain subdirectory. Placing it here
ensures that tests in /team/tests, user/tests, etc., can all access the same
shared testing setup, which is a pytest best practice for project wide fixtures.
"""

import pytest
from datetime import datetime
from CTFd.models import db as _db
from CTFd.cache import cache
from . import load as plugin_load
from .user.models.User import User as NgUser
from .event.models.Event import Event
from .team.controllers.create_team import create_team
from .team.controllers.join_team import join_team
from .permissions.controllers import assign_role_to_user
from .permissions.models.Role import Role
from .permissions.models.RolePermission import RolePermission
from .permissions.models.Permission import Permission
from .event_registration.controllers.create_event_registration import create_event_registration
from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
    gen_user,
)
from .core.testing.helpers import login_as


def create_app():
    """A reusable function to create the Flask app instance."""
    app = create_ctfd_original(enable_plugins=True, setup=False)
    with app.app_context():
        plugin_load(app)
    app = setup_ctfd(app)
    return app


@pytest.fixture(scope="session")
def app():
    """
    Session wide test Flask application.
    This is created only once for the test run.
    """
    _app = create_app()

    yield _app

    with _app.app_context():
        destroy_ctfd_original(_app)


@pytest.fixture(scope="function")
def middleware_client():
    """
    Creates an isolated, authenticated Flask app for testing middleware.
    It uses an in-memory database and cleans up after itself.
    Only used by tests marked with @pytest.mark.middleware.
    """
    from .core.testing.system.middleware_test_routes import middleware_test_routes

    app = create_ctfd_original(enable_plugins=True, setup=False)

    # Override the database configuration to use in memory sqlite for isolation
    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-for-sessions",
            "WTF_CSRF_ENABLED": False,
            "SERVER_NAME": None,
        }
    )

    with app.app_context():
        # Load our plugin isolated
        plugin_load(app)

        # Register ONLY our temporary test routes
        app.register_blueprint(middleware_test_routes)

        # Create the tables but in the sqlite db
        _db.create_all()

        # Minimal ctfd config
        from CTFd.models import Configs

        setup_config = Configs(key="setup", value="true")
        _db.session.add(setup_config)
        _db.session.commit()

        # Isolated context
        user_to_login = gen_user(_db, name="tempuser", email="tempuser@example.com")
        ng_user = NgUser(id=user_to_login.id)
        _db.session.add(ng_user)
        _db.session.commit()

        Role.create_role("Admin")
        Role.create_role("User")
        Permission.create_permission("CAN_EDIT_TEAM", "Edit team details")
        RolePermission.create_role_permission(1, 1)  # Admin role with all permissions

        assign_role_to_user(user_to_login.id, "Admin")

        user2 = gen_user(_db, name="tempuser2", email="user2@example.com")
        ng_user2 = NgUser(id=user2.id)
        _db.session.add(ng_user2)
        _db.session.commit()

        event = Event(name="Temp Event", description="Temporary event for testing")
        _db.session.add(event)
        _db.session.commit()

        event2 = Event(
            name="Second Temp Event",
            description="Another temporary event for testing",
            locked=True,
            start_time=datetime(2023, 1, 1),
            end_time=datetime(2023, 12, 31),
        )
        _db.session.add(event2)
        _db.session.commit()

        create_team(name="Temp Team", event_id=event.id, creator_id=user_to_login.id)
        create_team(name="Second Team", event_id=event.id, creator_id=user2.id)

        client = app.test_client()
        login_as(client, user_to_login)

        # Yield the authenticated client to the test
        yield client

    # Teardown happens automatically after yield


@pytest.fixture(scope="function")
def db_session(app, request):
    """
    Provides a clean database transaction for each test function
    that is marked with @pytest.mark.db.
    For tests not marked, it does nothing.
    """
    if "db" not in request.node.keywords:
        yield None
        return

    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()

        session = _db.create_scoped_session(options={"bind": connection, "binds": {}})
        _db.session = session

        # Clear any cached user data before test
        cache.clear()

        yield session

        session.remove()
        transaction.rollback()
        connection.close()

        # Clear cache after test to prevent state leakage
        cache.clear()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def logged_in_client(client, normal_user):
    """A test client that is logged in as a normal user."""
    login_as(client, normal_user)
    print(f"Logged in as user: {normal_user.name} (ID: {normal_user.id})")
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """A test client that is logged in as an admin user."""
    login_as(client, admin_user)
    return client


# Data Factory Fixtures


@pytest.fixture
def normal_user(db_session):
    """Creates a basic CTFd user and our plugin user."""
    if db_session is None:
        return None

    ctfd_user = gen_user(_db, name="testuser", email="test@example.com")
    ng_user = NgUser(id=ctfd_user.id)
    db_session.add(ng_user)
    db_session.commit()
    return ctfd_user


@pytest.fixture
def admin_user(db_session):
    """Creates an admin CTFd user and our plugin user."""
    if db_session is None:
        return None

    ctfd_user = gen_user(_db, name="admin", email="admin@example.com", type="admin")
    ng_user = NgUser(id=ctfd_user.id)
    db_session.add(ng_user)
    db_session.commit()
    return ctfd_user


@pytest.fixture
def event(db_session):
    """Creates a basic event."""
    if db_session is None:
        return None

    event = Event(name="Test Event", description="A event for testing")
    db_session.add(event)
    db_session.commit()
    return event


@pytest.fixture
def event2(db_session):
    """Creates a second event for multi-event tests."""
    if db_session is None:
        return None

    event = Event(name="Second Event", description="A second event for testing")
    db_session.add(event)
    db_session.commit()
    return event

@pytest.fixture
def event_registration(event, db_session):
    """Creates an event registration for the given event."""
    if db_session is None:
        return None

    result = create_event_registration(event_id=event.id, reg_open=True)
    if not result["success"]:
        raise Exception(f"Failed to create event registration: {result.get('error')}")

    return result["event_registration"]

@pytest.fixture
def closed_event_registration(event, db_session):
    """Creates a closed event registration for the given event."""
    if db_session is None:
        return None

    result = create_event_registration(event_id=event.id, reg_open=False)
    if not result["success"]:
        raise Exception(f"Failed to create event registration: {result.get('error')}")

    return result["event_registration"]

@pytest.fixture
def past_event_registration(event, db_session):
    """Creates an event registration for the given event with a past registration period."""
    if db_session is None:
        return None

    result = create_event_registration(event_id=event.id, reg_open=True, reg_start_date=datetime(2020, 1, 1), reg_end_date=datetime(2020, 1, 2))
    if not result["success"]:
        raise Exception(f"Failed to create past event registration: {result.get('error')}")

    return result["event_registration"]

@pytest.fixture
def future_event_registration(event, db_session):
    """Creates an event registration for the given event with a future registration period."""
    if db_session is None:
        return None

    result = create_event_registration(event_id=event.id, reg_open=True, reg_start_date=datetime(2125, 1, 1), reg_end_date=datetime(2125, 1, 2))
    if not result["success"]:
        raise Exception(f"Failed to create future event registration: {result.get('error')}")

    return result["event_registration"]



@pytest.fixture
def team(db_session, event, normal_user):
    """Creates a team with a normal user as the captain."""
    if db_session is None:
        return None

    result = create_team(name="Test Team", event_id=event.id, creator_id=normal_user.id)

    return result["team"]


@pytest.fixture
def team_with_members(db_session, event):
    """Creates a team with a captain and a regular member."""
    if db_session is None:
        return None

    # Create captain user (CTFd + plugin user)
    captain_ctfd = gen_user(_db, name="captain", email="captain@example.com")
    captain_ng = NgUser(id=captain_ctfd.id)
    db_session.add(captain_ng)
    db_session.commit()

    # Create member user (CTFd + plugin user)
    member_ctfd = gen_user(_db, name="member", email="member@example.com")
    member_ng = NgUser(id=member_ctfd.id)
    db_session.add(member_ng)
    db_session.commit()

    # Create team with captain as creator
    team_result = create_team(name="Test Team with Members", event_id=event.id, creator_id=captain_ctfd.id)
    team = team_result["team"]

    # Add member to the team using invite code
    invite_code = team_result["invite_code"]
    join_result = join_team(member_ctfd.id, invite_code)
    if not join_result["success"]:
        raise Exception(f"Failed to add member to team: {join_result.get('error')}")

    return {"team": team, "captain": captain_ctfd, "member": member_ctfd}


@pytest.fixture
def role_with_permissions(db_session):
    """Creates a role with permissions for testing."""
    if db_session is None:
        return None

    # Create a role
    role = Role.create_role("Test Role")

    # Create some permissions
    permission1 = Permission.create_permission("TEST_PERMISSION_1", "Test Permission 1")
    permission2 = Permission.create_permission("TEST_PERMISSION_2", "Test Permission 2")
    permission3 = Permission.create_permission("TEST_PERMISSION_3", "Test Permission 3")

    # Assign permissions to the role
    RolePermission.create_role_permission(role.id, permission1.id)
    RolePermission.create_role_permission(role.id, permission2.id)
    RolePermission.create_role_permission(role.id, permission3.id)

    db_session.commit()

    return role

@pytest.fixture
def user_with_roles(db_session):
    """Creates a user with multiple roles for testing."""
    if db_session is None:
        return None

    # Create a user
    user = gen_user(_db, name="testuser_with_roles", email="testuser_with_roles@example.com")
    ng_user = NgUser(id=user.id)
    db_session.add(ng_user)
    db_session.commit()

    # Assign multiple roles to the user
    role1 = Role.create_role("admin")
    role2 = Role.create_role("support")
    assign_role_to_user(user.id, role1.name)
    assign_role_to_user(user.id, role2.name)

    return user

@pytest.fixture
def permissions(db_session):

    if db_session is None:
        return None

    # Create some permissions
    permission1 = Permission.create_permission("TEST_PERMISSION_1", "Test Permission 1")
    permission2 = Permission.create_permission("TEST_PERMISSION_2", "Test Permission 2")
    permission3 = Permission.create_permission("TEST_PERMISSION_3", "Test Permission 3")

    db_session.commit()

    return [permission1, permission2, permission3]