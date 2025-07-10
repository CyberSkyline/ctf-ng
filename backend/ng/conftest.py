"""
Ctf-ng Pytest Fixtures
"""

import pytest
from datetime import datetime
from CTFd.models import db, Users
from CTFd.cache import cache
from CTFd.utils.security.csrf import generate_nonce
from . import load as plugin_load
from .user.models.User import User as NgUser
from .event.models.Event import Event
from .team.models.Team import Team
from .permissions.controllers import assign_role_to_user
from .permissions.models.Role import Role
from .permissions.models.RolePermission import RolePermission
from .permissions.models.Permission import Permission
from .core.tests.system.middleware_test_routes import middleware_test_routes
from .support.models.Ticket import Ticket
from .support.models.TicketTag import TicketTag
from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
    gen_user,
)
from .permissions.models.enums import PermissionEnum
from .permissions.models.enums import RoleEnum


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
    Creates and configures a new Flask application for the entire test session.
    """
    from .core.tests.helpers import create_ctfd, destroy_ctfd

    app = create_ctfd()
    yield app
    destroy_ctfd(app)



@pytest.fixture(scope="function")
def db_session(app):
    """
    Provides a clean database transaction for each test function
    that is marked with @pytest.mark.db.
    For tests not marked, it does nothing.
    """

    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.close()
        db.session = db.create_scoped_session(options={"bind": connection, "binds": {}})
        yield db.session
        transaction.rollback()
        connection.close()
        db.session.remove()


@pytest.fixture(scope="function")
def middleware_client():
    """
    Creates an isolated, authenticated Flask app for testing middleware.
    It uses an in-memory database and cleans up after itself.
    Only used by tests marked with @pytest.mark.middleware.
    """

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
        db.create_all()

        # Minimal ctfd config
        from CTFd.models import Configs

        setup_config = Configs(key="setup", value="true")
        db.session.add(setup_config)
        db.session.commit()

        # Isolated context
        user_to_login = gen_user(db, name="tempuser", email="tempuser@example.com")
        ng_user = NgUser(id=user_to_login.id)
        db.session.add(ng_user)
        db.session.commit()

        Role.create_role(RoleEnum.ADMIN)
        Role.create_role(RoleEnum.SUPPORT)
        Permission.create_permission(PermissionEnum.CAN_EDIT_TEAM, "Edit team details")
        RolePermission.create_role_permission(1, 1)  # Admin role with all permissions

        assign_role_to_user(user_to_login.id, RoleEnum.ADMIN)

        user2 = gen_user(db, name="tempuser2", email="user2@example.com")
        ng_user2 = NgUser(id=user2.id)
        db.session.add(ng_user2)
        db.session.commit()

        event = Event(name="Temp Event", description="Temporary event for testing")
        db.session.add(event)
        db.session.commit()

        event2 = Event(
            name="Second Temp Event",
            description="Another temporary event for testing",
            locked=True,
            start_time=datetime(2023, 1, 1),
            end_time=datetime(2023, 12, 31),
        )
        db.session.add(event2)
        db.session.commit()

        Team.create_team_with_captain(name="Temp Team", event_id=event.id, captain_id=user_to_login.id, invite_code="fo67ykug")
        Team.create_team_with_captain(name="Second Team", event_id=event.id, captain_id=user2.id)

        Ticket.create(
            subject="Test Ticket",
            author_id=user_to_login.id,
        )
        TicketTag.create(name="Test Tag")

        client = app.test_client()
        with client.session_transaction() as sess:
            sess["id"] = user_to_login.id
            sess["name"] = user_to_login.name
            sess["type"] = getattr(user_to_login, "type", "user")
            sess["nonce"] = "test-nonce"

        # Yield the authenticated client to the test
        yield client

    # Teardown happens automatically after yield


@pytest.fixture(scope="function")
def client(app, db_session):
    """A test client for making unauthenticated requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def user(db_session):
    """Creates a regular user in the database for testing."""
    user = Users(name="testuser", email="test@example.com", password="password")
    user.verified = True
    db_session.add(user)
    db_session.commit()
    from .user.models.User import User as NgUser

    NgUser.create_user(user_id=user.id, commit=False)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def admin(db_session):
    """Creates an admin user in the database for testing."""
    admin = Users(name="admin", email="admin@example.com", password="password", type="admin")
    admin.verified = True
    db_session.add(admin)
    db_session.commit()
    from .user.models.User import User as NgUser

    NgUser.create_user(user_id=admin.id, commit=False)
    db_session.commit()
    return admin


@pytest.fixture(scope="function")
def logged_in_client(app, db_session, user):
    """A test client logged in as a regular user."""
    # Clear any cached user data to prevent cross-test contamination
    from CTFd.cache import cache
    cache.clear()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        # Completely clear the session and set only what we need
        sess.clear()
        sess["id"] = user.id
        sess["name"] = user.name
        sess["type"] = user.type
        sess["nonce"] = generate_nonce()
        sess.permanent = False
    return client


@pytest.fixture(scope="function") 
def admin_client(app, db_session, admin):
    """A test client logged in as an admin."""
    # Clear any cached user data to prevent cross-test contamination
    from CTFd.cache import cache
    cache.clear()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        # Completely clear the session and set only what we need
        sess.clear()
        sess["id"] = admin.id
        sess["name"] = admin.name
        sess["type"] = admin.type
        sess["nonce"] = generate_nonce()
        sess.permanent = False
    return client


@pytest.fixture
def event_factory(db_session):
    """A factory function to create Event objects for tests."""
    from .event.models.Event import Event

    def _factory(**kwargs):
        defaults = {
            "name": f"Test Event {db_session.query(Event).count() + 1}",
            "description": "A test event.",
            "max_team_size": 4,
            "locked": False,
        }
        defaults.update(kwargs)
        event = Event.create_event(**defaults)
        return event

    return _factory


@pytest.fixture
def team_factory(db_session, event_factory):
    """A factory function to create Team objects for tests."""
    from .team.models.Team import Team
    from .team.models.TeamMember import TeamMember

    def _factory(event=None, **kwargs):
        members_to_add = kwargs.pop("members", [])

        if event is None:
            event = event_factory()

        defaults = {
            "name": f"Test Team {db_session.query(Team).count() + 1}",
            "event_id": event.id,
        }
        defaults.update(kwargs)
        team = Team.create_team(**defaults)

        for member_user in members_to_add:
            TeamMember.create_team_member(user_id=member_user.id, team_id=team.id, event_id=event.id)
        return team

    return _factory


@pytest.fixture
def event(event_factory):
    """Simple fixture to get a single event."""
    return event_factory()


@pytest.fixture
def open_event_reg(event, event_registration_factory, db_session):
    """An open event registration."""
    reg = event_registration_factory(event=event, reg_open=True)
    reg._test_event_id = event.id
    return reg


@pytest.fixture
def closed_event_reg(event, event_registration_factory, db_session):
    """A closed event registration."""
    reg = event_registration_factory(event=event, reg_open=False)
    reg._test_event_id = event.id
    return reg


@pytest.fixture
def past_event_reg(event, event_registration_factory, db_session):
    """An event registration with a registration window in the past."""
    reg = event_registration_factory(
        event=event,
        reg_start_date=datetime.utcnow() - timedelta(days=2),
        reg_end_date=datetime.utcnow() - timedelta(days=1),
    )
    db_session.expunge_all()
    db_session.add(reg)
    db_session.add(reg.event)
    db_session.commit()
    return reg


@pytest.fixture
def future_event_reg(event, event_registration_factory, db_session):
    """An event registration with a registration window in the future."""
    reg = event_registration_factory(
        event=event,
        reg_start_date=datetime.utcnow() + timedelta(days=1),
        reg_end_date=datetime.utcnow() + timedelta(days=2),
    )
    db_session.expunge_all()
    db_session.add(reg)
    db_session.add(reg.event)
    db_session.commit()
    return reg

@pytest.fixture
def role_with_permissions(db_session):
    """Creates a role with permissions for testing."""
    if db_session is None:
        return None

    # Create a role
    role = Role.create_role(RoleEnum.SUPPORT)

    # Create some permissions
    permission1 = Permission.create_permission(PermissionEnum.CAN_EDIT_TEAM, "Edit team details")
    permission2 = Permission.create_permission(PermissionEnum.CAN_EDIT_USER, "Edit user details")
    permission3 = Permission.create_permission(PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS, "Manage support tickets")

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
    user = gen_user(db, name="testuser_with_roles", email="testuser_with_roles@example.com")
    ng_user = NgUser(id=user.id)
    db_session.add(ng_user)
    db_session.commit()

    # Assign multiple roles to the user
    role1 = Role.create_role(RoleEnum.ADMIN)
    role2 = Role.create_role(RoleEnum.SUPPORT)
    assign_role_to_user(user.id, role1.name)
    assign_role_to_user(user.id, role2.name)

    return user

@pytest.fixture
def permissions(db_session):

    if db_session is None:
        return None

    # Create some permissions
    permission1 = Permission.create_permission(PermissionEnum.CAN_EDIT_TEAM, "Edit team details")
    permission2 = Permission.create_permission(PermissionEnum.CAN_EDIT_USER, "Edit user details")
    permission3 = Permission.create_permission(PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS, "Manage support tickets")

    db_session.commit()

    return [permission1, permission2, permission3]
