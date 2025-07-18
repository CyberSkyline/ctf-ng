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
def locked_event(db_session):
    """Create a locked event for testing restrictions."""
    from .event.models.Event import Event

    event = Event(
        name="Locked Event",
        description="This event is locked",
        locked=True,
        start_time=datetime.utcnow() - timedelta(days=10),
        end_time=datetime.utcnow() - timedelta(days=5)
    )
    db_session.add(event)
    db_session.commit()
    return event


@pytest.fixture
def future_event(db_session):
    """Create a future event that hasn't started yet."""
    from .event.models.Event import Event

    event = Event(
        name="Future Event",
        description="This event hasn't started",
        locked=False,
        start_time=datetime.utcnow() + timedelta(days=5),
        end_time=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(event)
    db_session.commit()
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
def challenge(db_session):
    """Create a test challenge for testing purposes."""
    challenge = Challenge(
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

    tag = TicketTag.create_tag(
        name="bug", color="#FF0000", description="Bug reports", commit=False
    )
    db_session.add(tag)
    db_session.commit()
    return tag


@pytest.fixture
def ticket_tag_factory(db_session):
    """Factory to create ticket tags"""
    from .support.models.TicketTag import TicketTag

    def _factory(**kwargs):
        defaults = {
            "name": f"tag_{datetime.utcnow().timestamp()}",
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

    ticket = Ticket.create_ticket(
        subject="Resolved Issue", author_id=user.id, commit=False
    )
    ticket.close_ticket(commit=False)
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def muted_ticket(db_session, user):
    """Creates a muted support ticket."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(
        subject="Low Priority Issue", author_id=user.id, commit=False
    )
    ticket.toggle_mute(True, commit=False)
    db_session.add(ticket)
    db_session.commit()
    return ticket


@pytest.fixture
def assigned_ticket(db_session, user, admin):
    """Creates a ticket assigned to an admin."""
    from .support.models.Ticket import Ticket

    ticket = Ticket.create_ticket(
        subject="Assigned Issue", author_id=user.id, commit=False
    )
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

    ticket.add_tags([tag1, tag2], commit=False)
    db_session.commit()
    return ticket


@pytest.fixture
def ticket_factory(db_session):
    """Factory to create tickets"""
    from .support.models.Ticket import Ticket

    def _factory(**kwargs):
        defaults = {
            "subject": f"Test Ticket {datetime.utcnow().timestamp()}",
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

    return _factory


@pytest.fixture
def multiple_tickets(db_session, user, admin, event, team_factory, ticket_factory):
    """Creates multiple tickets with various states for testing filters."""

    team = team_factory(event=event)

    tickets = {
        "open_unassigned": ticket_factory(
            subject="Open Unassigned", author_id=user.id, event_id=event.id
        ),
        "open_assigned": ticket_factory(
            subject="Open Assigned", author_id=user.id, team_id=team.id
        ),
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
        challenge_id=challenge.id,
        name="Test Question",
        body="What is 2+2?",
        answer="4",
        points=100,
        max_attempts=5
    )
    db_session.add(question)
    db_session.commit()
    return question


@pytest.fixture
def hint(db_session, challenge):
    """Create a test hint for scoring tests."""
    from .challenge.models.Hint import Hint

    hint = Hint(
        challenge_id=challenge.id,
        preview="Single digit hint",
        body="The answer is a single digit",
        deduction=20
    )
    db_session.add(hint)
    db_session.commit()
    return hint


@pytest.fixture
def team_with_member(db_session, event, user):
    """Create a team with a member for scoring tests."""
    from .team.models.Team import Team

    team = Team.create_team_with_captain(
        name="Test Scoring Team",
        event_id=event.id,
        captain_id=user.id,
        invite_code="test123"
    )
    return team


@pytest.fixture
def score(db_session, team_with_member, event):
    """Create a Score record for testing."""
    from .scoring.models.Score import Score

    existing_score = Score.query.filter_by(
        team_id=team_with_member.id,
        event_id=event.id
    ).first()

    if existing_score:
        return existing_score

    score = Score.create_score(
        team_id=team_with_member.id,
        event_id=event.id,
        team_name=team_with_member.name,
        commit=False
    )
    db_session.commit()
    return score


@pytest.fixture
def score_event(db_session, score, team_with_member):
    """Create a ScoreEvent for testing."""
    from .scoring.models.ScoreEvent import ScoreEvent

    score_event = ScoreEvent(
        score_id=score.id,
        team_id=team_with_member.id,
        points=50,
        timestamp=datetime.utcnow()
    )
    db_session.add(score_event)
    db_session.commit()
    score.adjust(50, commit=True)
    return score_event


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
            "timestamp": kwargs.get("timestamp", datetime.utcnow())
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
            "timestamp": kwargs.get("timestamp", datetime.utcnow())
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
            "timestamp": kwargs.get("timestamp", datetime.utcnow())
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
            "last_update": kwargs.get("last_update", datetime.utcnow()),
            "team_name": kwargs.get("team_name", "Test Team")
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
            "timestamp": kwargs.get("timestamp", datetime.utcnow())
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
            password="password"
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
            invite_code=f"score{i}123"
        )

        score = Score.query.filter_by(team_id=team.id, event_id=event.id).first()
        score.points = (i + 1) * 100
        db_session.commit()

        teams_data.append({
            "user_id": user_ids[i],
            "team": team,
            "score": score
        })

    return teams_data
