# /plugin/tests/conftest.py

import pytest
from CTFd.models import db as _db
from plugin import load as plugin_load
from plugin.models import User as NgUser
from tests.helpers import (
    create_ctfd as create_ctfd_original,
    destroy_ctfd as destroy_ctfd_original,
    setup_ctfd,
    gen_user,
)


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
        from CTFd.cache import cache

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
    from .helpers import login_as

    login_as(client, normal_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """A test client that is logged in as an admin user."""
    from .helpers import login_as

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
def world(db_session):
    """Creates a basic world."""
    if db_session is None:
        return None
    from plugin.models import World

    world = World(name="Test World", description="A world for testing")
    db_session.add(world)
    db_session.commit()
    return world


@pytest.fixture
def team(db_session, world, normal_user):
    """Creates a team with a normal user as the captain."""
    if db_session is None:
        return None
    from plugin.controllers.team_controller import TeamController

    result = TeamController.create_team(name="Test Team", world_id=world.id, creator_id=normal_user.id)
    # The controller returns a dictionary, we want the model instance
    return result["team"]


@pytest.fixture
def team_with_members(db_session, world):
    """Creates a team with a captain and a regular member."""
    if db_session is None:
        return None
    from plugin.controllers.team_controller import TeamController

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
    team_result = TeamController.create_team(
        name="Test Team with Members", world_id=world.id, creator_id=captain_ctfd.id
    )
    team = team_result["team"]

    # Add member to the team
    join_result = TeamController.join_team(member_ctfd.id, team.id, world.id)
    if not join_result["success"]:
        raise Exception(f"Failed to add member to team: {join_result.get('error')}")

    return {"team": team, "captain": captain_ctfd, "member": member_ctfd}
