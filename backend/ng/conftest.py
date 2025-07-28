"""
Ctf-ng Pytest Fixtures
"""

from datetime import datetime, timedelta

import pytest
from CTFd.cache import cache
from CTFd.models import Configs, Users, db
from CTFd.utils.security.csrf import generate_nonce
from tests.helpers import (
    create_ctfd as create_ctfd_original,
)
from tests.helpers import (
    gen_user,
    setup_ctfd,
)

from . import load as plugin_load
from .challenge.models.Challenge import Challenge
from .core.tests.helpers import create_ctfd, destroy_ctfd
from .core.tests.system.middleware_test_routes import middleware_test_routes
from .event.models.Event import Event
from .permissions.controllers import assign_role_to_user
from .permissions.models.enums import PermissionEnum, RoleEnum
from .permissions.models.Permission import Permission
from .permissions.models.Role import Role
from .permissions.models.RolePermission import RolePermission
from .support.models.Ticket import Ticket
from .support.models.TicketTag import TicketTag
from .team.models.Team import Team
from .user.models.User import User as NgUser
from .event.models.Demographic import Demographic


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

        event = Event(name="Temp Event", description="Temporary event for testing",public=True,)
        db.session.add(event)
        db.session.commit()

        event2 = Event(
            name="Second Temp Event",
            description="Another temporary event for testing",
            locked=True,
            start_time=datetime(2023, 1, 1),
            end_time=datetime(2023, 12, 31),
            public=False,
        )
        db.session.add(event2)
        db.session.commit()

        event3 = Event(
            name="Third Temp Event",
            description="Third temporary event for testing",
            locked=False,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            public=False,
        )
        db.session.add(event3)
        db.session.commit()

        Demographic.create_demographic(
            user_id=user_to_login.id, event_id = event3.id, commit=True
        )

        Team.create_team_with_captain(
            name="Temp Team", event_id=event.id, captain_id=user_to_login.id, invite_code="fo67ykug"
        )
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
            "start_time": datetime.utcnow() - timedelta(days=1),
            "end_time": datetime.utcnow() + timedelta(days=1),
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
        captain = members_to_add.pop(0)

        if event is None:
            event = event_factory()

        defaults = {
            "name": f"Test Team {db_session.query(Team).count() + 1}",
            "event_id": event.id,
            "captain_id": captain.id,
        }
        defaults.update(kwargs)
        team = Team.create_team_with_captain(**defaults)

        for member_user in members_to_add:
            TeamMember.create_team_member(user_id=member_user.id, team_id=team.id, event_id=event.id)
            Demographic.create_demographic(
                user_id=member_user.id, event_id=event.id, commit=False
            )
        return team

    return _factory

@pytest.fixture
def user_factory(db_session):
    """A factory function to create User objects for tests."""
    from .user.models.User import User

    def _factory(name="Test User", email="testuser@example.com", password="password"):
        user = Users(name=name, email=email)
        db_session.add(user)
        db_session.commit()

        ng_user = User(id=user.id)
        db_session.add(ng_user)
        db_session.commit()
        return ng_user

    return _factory


@pytest.fixture
def team_with_member(db_session, team_factory, user):
    """Creates a team with members for testing."""
    team = team_factory(members=[user])
    return team

@pytest.fixture
def team_with_members(db_session, team_factory, user_factory):
    """Creates a team with multiple members for testing."""
    users = [user_factory(name=f"User {i}", email=f"user{i}@example.com") for i in range(1, 4)]
    team = team_factory(members=users)
    return team

@pytest.fixture
def team_captain_client(app, db_session, team_with_members, role_with_permissions):
    """A test client logged in as a team captain."""
    # Clear any cached user data to prevent cross-test contamination
    from CTFd.cache import cache
    cache.clear()
    client = app.test_client()
    with client.session_transaction() as sess:
        # Completely clear the session and set only what we need
        sess.clear()
        sess["id"] = team_with_members.members[0].user_id
        sess["name"] = team_with_members.members[0].user.ctfd_user.name
        sess["type"] = "team"
        sess["nonce"] = generate_nonce()
        sess.permanent = False
    return client

@pytest.fixture
def team_member_client(app, db_session, team_with_members, role_with_permissions):
    """A test client logged in as a team member."""
    # Clear any cached user data to prevent cross-test contamination
    from CTFd.cache import cache
    cache.clear()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        # Completely clear the session and set only what we need
        sess.clear()
        sess["id"] = team_with_members.members[1].user_id
        sess["name"] = team_with_members.members[1].user.ctfd_user.name
        sess["type"] = "team"
        sess["nonce"] = generate_nonce()
        sess.permanent = False
    return client

@pytest.fixture
def closed_event_client(app, db_session, event_factory, team_factory, user_factory):
    """A test client for a closed event."""
    # Clear any cached user data to prevent cross-test contamination
    from CTFd.cache import cache
    cache.clear()
    user = user_factory(name="Closed Event User", email="closed_event_user@example.com")
    user2 = user_factory(name="Closed Event User 2", email="closed_event_user2@example.com")
    event = event_factory(locked=True, start_time=datetime.utcnow() - timedelta(days=2), end_time=datetime.utcnow() - timedelta(days=1))
    team = team_factory(event=event, members=[user, user2])

    client = app.test_client()
    with client.session_transaction() as sess:
        # Completely clear the session and set only what we need
        sess.clear()
        sess["id"] = team.members[0].user_id
        sess["name"] = team.members[0].user.ctfd_user.name
        sess["type"] = "team"
        sess["nonce"] = generate_nonce()
        sess.permanent = False
    return client


@pytest.fixture
def event(event_factory):
    """Simple fixture to get a single event."""
    return event_factory()





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


@pytest.fixture
def challenge(db_session, event):
    """Create a test challenge for testing purposes."""
    challenge = Challenge(
        event_id=event.id,
        name="Test Challenge",
        description="A test challenge for question testing",
        icon="test-icon",
        summary="Test summary",
    )
    db_session.add(challenge)
    db_session.commit()
    return challenge


@pytest.fixture
def challenge_factory(db_session, event_factory):
    """A factory function to create Challenge objects for tests, with 2 questions."""

    from .challenge.models.Question import Question

    def _factory(event=None, **kwargs):
        if event is None:
            event = event_factory()
        defaults = {
            "event_id": event.id,
            "name": f"Test Challenge {db_session.query(Challenge).count() + 1}",
            "description": "A test challenge for question testing",
            "icon": "test-icon",
            "summary": "Test summary",
        }
        defaults.update(kwargs)
        challenge = Challenge(**defaults)
        db_session.add(challenge)
        db_session.commit()

        # Create 2 questions for this challenge
        for i in range(2):
            question = Question(
                challenge_id=challenge.id,
                name=f"Test Question {i + 1} for Challenge {challenge.id}",
                body=f"test question body_{i + 1}",
                answer=f"answer_{i + 1}",
                points=100 * (i + 1),
                placeholder=f"placeholder_{i + 1}",
                max_attempts=3,
            )
            db_session.add(question)
        db_session.commit()

        return challenge

    return _factory


@pytest.fixture
def question_factory(db_session, challenge_factory):
    """A factory function to create Question objects for tests."""

    from .challenge.models.Question import Question

    def _factory(challenge=None, **kwargs):
        if challenge is None:
            challenge = challenge_factory()
        count = db_session.query(Question).count() + 1

        defaults = {
            "challenge_id": challenge.id,
            "name": f"Test Question {count} for Challenge {challenge.id}",
            "body": f"test question body_{count}",
            "answer": f"answer_{count}",
            "points": 100 * count,
            "placeholder": f"placeholder_{count}",
            "max_attempts": 3,
        }
        defaults.update(kwargs)
        question = Question(**defaults)
        db_session.add(question)
        db_session.commit()
        return question

    return _factory
