"""
Ctf-ng Pytest Fixtures
"""

import pytest
from CTFd.models import db, Users
from CTFd.utils.security.csrf import generate_nonce
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def app():
    """
    Creates and configures a new Flask application for the entire test session.
    """
    from .core.testing.helpers import create_ctfd, destroy_ctfd

    app = create_ctfd()
    yield app
    destroy_ctfd(app)


@pytest.fixture(scope="function")
def db_session(app):
    """
    Transactional database session for each test function.
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


@pytest.fixture
def logged_in_client(app, client, user):
    """A test client logged in as a regular user."""
    with client.session_transaction() as sess:
        sess["id"] = user.id
        sess["name"] = user.name
        sess["type"] = user.type
        sess["nonce"] = generate_nonce()
    return client


@pytest.fixture
def admin_client(app, client, admin):
    """A test client logged in as an admin."""
    with client.session_transaction() as sess:
        sess["id"] = admin.id
        sess["name"] = admin.name
        sess["type"] = admin.type
        sess["nonce"] = generate_nonce()
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
    from .team.controllers._generate_invite_code import _generate_invite_code

    def _factory(event=None, **kwargs):
        members_to_add = kwargs.pop("members", [])

        if event is None:
            event = event_factory()

        defaults = {
            "name": f"Test Team {db_session.query(Team).count() + 1}",
            "event_id": event.id,
            "invite_code": _generate_invite_code(),
        }
        defaults.update(kwargs)
        team = Team.create_team(**defaults)

        for member_user in members_to_add:
            TeamMember.create_team_member(user_id=member_user.id, team_id=team.id, event_id=event.id)
        return team

    return _factory


@pytest.fixture
def event_registration_factory(db_session, event_factory):
    """A factory to create EventRegistration objects."""
    from .event_registration.models.EventRegistration import EventRegistration

    def _factory(event=None, **kwargs):
        if event is None:
            event = event_factory()

        if event not in db_session:
            event = db_session.merge(event)

        defaults = {
            "event_id": event.id,
            "reg_open": True,
            "public": True,
            "reg_start_date": None,
            "reg_end_date": None,
        }
        defaults.update(kwargs)
        reg = EventRegistration(**defaults)
        db_session.add(reg)
        db_session.commit()

        db_session.refresh(reg)
        return reg

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
