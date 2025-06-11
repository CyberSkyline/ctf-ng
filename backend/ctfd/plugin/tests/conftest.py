"""
/backend/ctfd/plugin/tests/conftest.py
Defines shared Pytest fixtures for application setup.
"""

import pytest
from CTFd.models import db as _db
from CTFd.cache import cache

from plugin import load as plugin_load
from plugin.user.models.User import User as NgUser
from plugin.event.models.Event import Event
from plugin.team.controllers import create_team, join_team
from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
    gen_user,
)
from .helpers import login_as


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
    with _app.app_context():
        _db.create_all()

    yield _app

    with _app.app_context():
        destroy_ctfd_original(_app)


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
