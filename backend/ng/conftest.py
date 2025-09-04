"""
Ctf-ng Pytest Fixtures
"""

from datetime import datetime, timezone, timedelta, UTC

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
from .event.models.Demographic import Demographic
from .event.models.Event import Event
from .permissions.controllers import assign_role_to_user
from .permissions.models.enums import PermissionEnum, RoleEnum
from .permissions.models.Permission import Permission
from .permissions.models.Role import Role
from .permissions.models.RolePermission import RolePermission
from .permissions.controllers.assign_role_to_user import assign_role_to_user
from .support.models.Ticket import Ticket
from .support.models.TicketTag import TicketTag
from .team.models.Team import Team
from .user.models.User import User as NgUser
from .core.utils import utc_now


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
        Role.create_role(RoleEnum.ADMIN)
        Permission.create_permission(PermissionEnum.CAN_IMPERSONATE_USERS, "Impersonate users")
        Permission.create_permission(PermissionEnum.CAN_EDIT_TEAM, "Edit team details")
        Permission.create_permission(PermissionEnum.CAN_EDIT_USER, "Edit user details")
        Permission.create_permission(PermissionEnum.CAN_VIEW_CHALLENGES, "View challenges")
        Permission.create_permission(PermissionEnum.CAN_PLAY_CHALLENGES, "Play challenges")
        Permission.create_permission(PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS, "Manage support tickets")
        RolePermission.create_role_permission(1, 1)
        RolePermission.create_role_permission(1, 2)
        RolePermission.create_role_permission(1, 3)
        RolePermission.create_role_permission(1, 4)
        RolePermission.create_role_permission(1, 5)
        RolePermission.create_role_permission(1, 6)
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
        Permission.create_permission(PermissionEnum.CAN_EDIT_USER, "Edit user details")
        Permission.create_permission(PermissionEnum.CAN_MANAGE_SUPPORT_TICKETS, "Manage support tickets")
        RolePermission.create_role_permission(1, 1)
        RolePermission.create_role_permission(1, 2)
        RolePermission.create_role_permission(1, 3)

        assign_role_to_user(user_to_login.id, RoleEnum.ADMIN)

        user2 = gen_user(db, name="tempuser2", email="user2@example.com")
        ng_user2 = NgUser(id=user2.id)
        db.session.add(ng_user2)
        db.session.commit()

        event = Event(
            name="Temp Event",
            description="Temporary event for testing",
            public=True,
        )
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

        Demographic.create_demographic(user_id=user_to_login.id, event_id=event3.id, commit=True)

        team = Team.create_team_with_captain(
            name="Temp Team", event_id=event.id, captain_id=user_to_login.id, invite_code="fo67ykug"
        )

        team.set_start_timestamp(datetime.now())

        Team.create_team_with_captain(name="Second Team", event_id=event.id, captain_id=user2.id)

        team3 = Team.create_team_with_captain(name="Third Team", event_id=event2.id, captain_id=user2.id)
        team3.set_start_timestamp(datetime.now())

        Ticket.create_ticket(
            subject="Test Ticket",
            author_id=user_to_login.id,
        )
        TicketTag.create_tag(name="Test Tag")

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
    db_session.flush()
    from .user.models.User import User as NgUser

    NgUser.create_user(user_id=user.id, commit=False)
    db_session.flush()
    return user



@pytest.fixture(scope="function")
def admin(db_session):
    """Creates an admin user in the database for testing."""
    admin = Users(name="admin", email="admin@example.com", password="password", type="admin")
    admin.verified = True
    db_session.add(admin)
    db_session.flush()

    NgUser.create_user(user_id=admin.id, commit=False)
    assign_role_to_user(admin.id, RoleEnum.ADMIN)
    db_session.flush()
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
            "start_time": utc_now() - timedelta(days=1),
            "end_time": utc_now() + timedelta(days=1),
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
            Demographic.create_demographic(user_id=member_user.id, event_id=event.id, commit=False)
        return team

    return _factory


@pytest.fixture
def user_factory(db_session):
    """A factory function to create User objects for tests."""
    from .user.models.User import User

    def _factory(name="Test User", email="testuser@example.com", password="password", admin=False):
        user = Users(name=name, email=email)
        db_session.add(user)
        db_session.commit()

        ng_user = User(id=user.id)
        db_session.add(ng_user)
        if admin:
            assign_role_to_user(ng_user.id, RoleEnum.ADMIN)
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
def started_player_client(app, db_session, team_with_members, role_with_permissions):
    """A test client logged in as a player who has started the event."""

    from CTFd.cache import cache

    cache.clear()
    team_with_members.set_start_timestamp(utc_now() - timedelta(hours=1))
    client = app.test_client()
    with client.session_transaction() as sess:
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
    event = event_factory(
        locked=True, start_time=utc_now() - timedelta(days=2), end_time=utc_now() - timedelta(days=1)
    )
    team = team_factory(event=event, members=[user, user2])
    team.set_start_timestamp(utc_now() - timedelta(days=2))

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
def event(db_session):
    """Simple fixture to get a single event."""
    from .event.models.Event import Event

    event = Event(
        name=f"Test Event {db_session.query(Event).count() + 1}",
        description="A test event.",
        max_team_size=4,
        locked=False,
    )
    db_session.add(event)
    db_session.flush()
    return event


@pytest.fixture
def locked_event(db_session):
    """Create a locked event for testing restrictions."""
    from .event.models.Event import Event

    event = Event(
        name="Locked Event",
        description="This event is locked",
        locked=True,
        start_time=utc_now() - timedelta(days=10),
        end_time=utc_now() - timedelta(days=5),
    )
    db_session.add(event)
    db_session.flush()
    return event


@pytest.fixture
def future_event(db_session):
    """Create a future event that hasn't started yet."""
    from .event.models.Event import Event

    event = Event(
        name="Future Event",
        description="This event hasn't started",
        locked=False,
        start_time=utc_now() + timedelta(days=5),
        end_time=utc_now() + timedelta(days=10),
    )
    db_session.add(event)
    db_session.flush()
    return event


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
    Role.create_role(RoleEnum.ADMIN)
    Role.create_role(RoleEnum.SUPPORT)
    assign_role_to_user(user.id, RoleEnum.ADMIN)
    assign_role_to_user(user.id, RoleEnum.SUPPORT)

    return user



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
def ticket_tag(db_session):
    """Creates a ticket tag for testing."""
    from .support.models.TicketTag import TicketTag

    tag = TicketTag.create_tag(name="bug", color="#FF0000", description="Bug reports", commit=False)
    db_session.add(tag)
    db_session.commit()
    return tag


@pytest.fixture
def ticket_tag_factory(db_session):
    """Factory to create ticket tags"""
    from .support.models.TicketTag import TicketTag

    def _factory(**kwargs):
        defaults = {
            "name": f"tag_{utc_now().timestamp()}",
            "color": "#0000FF",
            "description": "Test tag",
        }
        defaults.update(kwargs)

        tag = TicketTag.create_tag(**defaults, commit=False)
        db_session.add(tag)
        db_session.commit()
        return tag

    return _factory


@pytest.fixture
def ticket(db_session, user, event):
    """Creates a basic support ticket."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(
        subject="Test Support Request",
        author_id=user.id,
        event_id=event.id,
        commit=False,
    )
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def closed_ticket(db_session, user):
    """Creates a closed support ticket."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(subject="Resolved Issue", author_id=user.id, commit=False)
    ticket.close_ticket(commit=False)
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def muted_ticket(db_session, user):
    """Creates a muted support ticket."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(subject="Low Priority Issue", author_id=user.id, commit=False)
    ticket.toggle_mute(True, commit=False)
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def assigned_ticket(db_session, user, admin):
    """Creates a ticket assigned to an admin."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(subject="Assigned Issue", author_id=user.id, commit=False)
    ticket.assign_to_user(admin.id, commit=False)
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def ticket_with_messages(db_session, ticket, user, admin):
    """Creates a ticket with messages from user and admin."""
    from .support.models.TicketMessage import TicketMessage

    user_msg = TicketMessage.create_message(
        text="I'm having an issue", ticket_id=ticket.id, author_id=user.id, commit=False
    )

    admin_msg = TicketMessage.create_message(
        text="I'll help you", ticket_id=ticket.id, author_id=admin.id, commit=False
    )

    ticket.first_admin_response_timestamp = admin_msg.created_at

    db_session.add_all([user_msg, admin_msg])
    db_session.commit()
    return ticket


@pytest.fixture
def ticket_with_tags(db_session, ticket, ticket_tag_factory):
    """Creates a ticket with multiple tags."""

    tag1 = ticket_tag_factory(name="urgent")
    tag2 = ticket_tag_factory(name="technical")

    ticket.set_tags([tag1.id, tag2.id], commit=False)
    db_session.commit()
    return ticket


@pytest.fixture
def ticket_factory(db_session):
    """Factory to create tickets"""
    from .support.models.Ticket import Ticket

    def _factory(**kwargs):
        defaults = {
            "subject": f"Test Ticket {utc_now().timestamp()}",
            "author_id": kwargs.get("author_id", 1),
        }
        defaults.update(kwargs)

        ticket = Ticket.create_ticket(**defaults, commit=False)
        db_session.add(ticket)
        db_session.commit()
        return ticket

    return _factory


@pytest.fixture
def ticket_message_factory(db_session):
    """Factory to create ticket messages"""
    from .support.models.TicketMessage import TicketMessage

    def _factory(**kwargs):
        defaults = {
            "text": "Test message",
            "ticket_id": kwargs.get("ticket_id", 1),
            "author_id": kwargs.get("author_id", 1),
        }
        defaults.update(kwargs)

        message = TicketMessage.create_message(**defaults, commit=False)
        db_session.add(message)
        db_session.commit()
        return message

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
def multiple_tickets(db_session, user, admin, event, team_factory, ticket_factory):
    """Creates multiple tickets with various states for testing filters."""

    team = team_factory(event=event, members=[user])

    tickets = {
        "open_unassigned": ticket_factory(subject="Open Unassigned", author_id=user.id, event_id=event.id),
        "open_assigned": ticket_factory(subject="Open Assigned", author_id=user.id, team_id=team.id),
        "closed": ticket_factory(subject="Closed Ticket", author_id=admin.id),
        "muted": ticket_factory(subject="Muted Ticket", author_id=user.id),
    }

    tickets["open_assigned"].assign_to_user(admin.id)
    tickets["closed"].close_ticket()
    tickets["muted"].toggle_mute(True)

    return tickets


# Scoring Module Fixtures


@pytest.fixture
def question(db_session, challenge):
    """Create a test question for scoring tests."""
    from .challenge.models.Question import Question

    question = Question(
        challenge_id=challenge.id, name="Test Question", body="What is 2+2?", answer="4", points=100, max_attempts=5
    )
    db_session.add(question)
    db_session.commit()
    return question


@pytest.fixture
def hint(db_session, challenge):
    """Create a test hint for scoring tests."""
    from .challenge.models.Hint import Hint

    hint = Hint(
        challenge_id=challenge.id, preview="Single digit hint", body="The answer is a single digit", deduction=20
    )
    db_session.add(hint)
    db_session.commit()
    return hint


@pytest.fixture
def team_with_member(db_session, event, user):
    """Create a team with a member for scoring tests."""
    from .team.models.Team import Team

    event_id = event.id
    team = Team.create_team_with_captain(
        name="Test Scoring Team", event_id=event_id, captain_id=user.id, invite_code="test123"
    )
    return team


@pytest.fixture
def score(db_session, team_with_member, event):
    """Get the Score record that was automatically created with the team."""
    from .scoring.models.Score import Score

    score = Score.query.filter_by(team_id=team_with_member.id, event_id=event.id).first()

    if not score:
        raise RuntimeError("Score should have been created automatically with team")

    return score


@pytest.fixture
def score_event(db_session, score, team_with_member):
    """Create a ScoreEvent for testing."""
    from .scoring.models.ScoreEvent import ScoreEvent

    score_event = ScoreEvent(score_id=score.id, team_id=team_with_member.id, points=50, timestamp=utc_now())
    db_session.add(score_event)
    db_session.commit()
    score.adjust(50, commit=True)
    return score_event

@pytest.fixture
def hint_factory(db_session):

    from .challenge.models.Hint import Hint
    def _factory(**kwargs):
        defaults = {
            "challenge_id": kwargs.get("challenge_id", 1),
            "preview": kwargs.get("preview", "Test preview"),
            "body": kwargs.get("body", "Test body"),
            "deduction": kwargs.get("deduction", 10),
        }
        defaults.update(kwargs)

        hint = Hint(**defaults)
        db_session.add(hint)
        if kwargs.get("commit", True):
            db_session.commit()
        return hint

    return _factory


@pytest.fixture
def attempt_factory(db_session):
    """Factory to create attempts."""
    from .scoring.models.Attempt import Attempt

    def _factory(**kwargs):
        defaults = {
            "user_id": kwargs.get("user_id", 1),
            "team_id": kwargs.get("team_id", 1),
            "event_id": kwargs.get("event_id", 1),
            "challenge_id": kwargs.get("challenge_id", 1),
            "question_id": kwargs.get("question_id", 1),
            "submission": kwargs.get("submission", "test answer"),
            "is_correct": kwargs.get("is_correct", False),
            "points": kwargs.get("points", 0),
            "timestamp": kwargs.get("timestamp", utc_now()),
        }
        defaults.update(kwargs)

        attempt = Attempt(**defaults)
        db_session.add(attempt)
        if kwargs.get("commit", True):
            db_session.commit()
        return attempt

    return _factory


@pytest.fixture
def hint_redemption_factory(db_session):
    """Factory to create hint redemptions."""
    from .scoring.models.HintRedemption import HintRedemption

    def _factory(**kwargs):
        defaults = {
            "hint_id": kwargs.get("hint_id", 1),
            "user_id": kwargs.get("user_id", 1),
            "team_id": kwargs.get("team_id", 1),
            "points": kwargs.get("points", 0),
            "timestamp": kwargs.get("timestamp", utc_now()),
        }
        defaults.update(kwargs)

        redemption = HintRedemption(**defaults)
        db_session.add(redemption)
        if kwargs.get("commit", True):
            db_session.commit()
        return redemption

    return _factory


@pytest.fixture
def manual_award_factory(db_session):
    """Factory to create manual point awards."""
    from .scoring.models.ManualPointAward import ManualPointAward

    def _factory(**kwargs):
        defaults = {
            "admin_id": kwargs.get("admin_id", 1),
            "team_id": kwargs.get("team_id", 1),
            "points": kwargs.get("points", 100),
            "reason": kwargs.get("reason", "Test award"),
            "timestamp": kwargs.get("timestamp", utc_now()),
        }
        defaults.update(kwargs)

        award = ManualPointAward(**defaults)
        db_session.add(award)
        if kwargs.get("commit", True):
            db_session.commit()
        return award

    return _factory


@pytest.fixture
def score_factory(db_session):
    """Factory to create Score records."""
    from .scoring.models.Score import Score

    def _factory(**kwargs):
        defaults = {
            "team_id": kwargs.get("team_id", 1),
            "event_id": kwargs.get("event_id", 1),
            "points": kwargs.get("points", 0),
            "last_update": kwargs.get("last_update", utc_now()),
            "team_name": kwargs.get("team_name", "Test Team"),
        }
        defaults.update(kwargs)

        score = Score(**defaults)
        db_session.add(score)
        if kwargs.get("commit", True):
            db_session.commit()
        return score

    return _factory


@pytest.fixture
def score_event_factory(db_session):
    """Factory to create ScoreEvent records."""
    from .scoring.models.ScoreEvent import ScoreEvent

    def _factory(**kwargs):
        defaults = {
            "score_id": kwargs.get("score_id", 1),
            "team_id": kwargs.get("team_id", 1),
            "points": kwargs.get("points", 100),
            "timestamp": kwargs.get("timestamp", utc_now()),
        }
        defaults.update(kwargs)

        score_event = ScoreEvent(**defaults)
        db_session.add(score_event)
        if kwargs.get("commit", True):
            db_session.commit()
        return score_event

    return _factory


@pytest.fixture
def multiple_teams_with_scores(db_session, event, team_factory, score_factory):
    """Create multiple teams with different scores for leaderboard testing."""
    from .scoring.models.Score import Score

    teams_data = []

    user_ids = []
    for i in range(5):
        user = Users(
            name=f"scoreuser{i}",
            email=f"scoreuser{i}@example.com",
            password="password",
        )
        user.verified = True
        db_session.add(user)
        db_session.commit()

        ng_user = NgUser(id=user.id)
        db_session.add(ng_user)
        db_session.commit()
        user_ids.append(user.id)

    for i in range(5):
        team = Team.create_team_with_captain(
            name=f"Score Team {i}",
            event_id=event.id,
            captain_id=user_ids[i],
            invite_code=f"score{i}123",
        )

        score = Score.query.filter_by(team_id=team.id, event_id=event.id).first()
        score.points = (i + 1) * 100
        db_session.commit()

        teams_data.append(
            {
                "user_id": user_ids[i],
                "team": team,
                "score": score,
            }
        )

    return teams_data

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


@pytest.fixture
def notification_factory(db_session):
    """
    Factory to create notifications
    """
    from .notifications.models.Notification import Notification, NotificationType

    def _factory(**kwargs):
        defaults = {
            "type": kwargs.get("type", NotificationType.TICKET_CREATE),
            "title": kwargs.get("title", f"Test Notification {datetime.utcnow().timestamp()}"),
            "message": kwargs.get("message", "Test notification message"),
            "recipient_id": kwargs.get("recipient_id", 1),
            "sender_id": kwargs.get("sender_id", None),
            "read_at": kwargs.get("read_at", None),
            "created_at": kwargs.get("created_at", datetime.now(UTC)),
            "expires_at": kwargs.get("expires_at", None),
            "ticket_id": kwargs.get("ticket_id", None),
            "team_id": kwargs.get("team_id", None),
            "event_id": kwargs.get("event_id", None),
            "challenge_id": kwargs.get("challenge_id", None),
        }
        defaults.update(kwargs)

        notification = Notification(**defaults)
        db_session.add(notification)
        if kwargs.get("commit", True):
            db_session.commit()
        return notification

    return _factory


@pytest.fixture
def announcement_factory(db_session):
    """
    Factory to create announcements
    """
    from .notifications.models.Announcement import Announcement, AnnouncementType

    def _factory(**kwargs):
        defaults = {
            "type": kwargs.get("type", AnnouncementType.GENERAL),
            "title": kwargs.get("title", f"Test Announcement {datetime.utcnow().timestamp()}"),
            "message": kwargs.get("message", "Test announcement message"),
            "sender_id": kwargs.get("sender_id", None),
            "created_at": kwargs.get("created_at", datetime.now(UTC)),
            "expires_at": kwargs.get("expires_at", None),
            "event_id": kwargs.get("event_id", None),
        }
        defaults.update(kwargs)

        announcement = Announcement(**defaults)
        db_session.add(announcement)
        if kwargs.get("commit", True):
            db_session.commit()
        return announcement

    return _factory
