#!/usr/bin/env python3

import os

from CTFd import create_app, CTFdFlask
from CTFd.cache import cache
from CTFd.config import Config
from CTFd.models import Users, db
from sqlalchemy_utils import create_database, database_exists, drop_database
from tests.helpers import setup_ctfd
from .populate_load_testing_data import populate_load_testing_data

if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

if "LOAD_TEST" not in os.environ:
    raise OSError("LOAD_TEST environment variable not set. Absorting...")

DEFAULT_ADMIN_EMAIL = "admin@examplectf.com"
DEFAULT_ADMIN_PASSWORD = "ctfng_password"

# Get the database URL from default config
database_url = Config.SQLALCHEMY_DATABASE_URI

# Drop and recreate database BEFORE creating the app
if database_exists(database_url):
    drop_database(database_url)

# Recreate the database
create_database(database_url)

# Now create the app - it won't try to create tables in an existing database
app: CTFdFlask = create_app()

with app.app_context():
    # Clear cache
    cache.clear()

    # Create all tables
    db.create_all()

    # Commit the changes
    db.session.commit()

    # Perform the default setup
    app = setup_ctfd(
        app,
        ctf_name="CTFd",
        ctf_description="CTF description",
        name="admin",
        email=DEFAULT_ADMIN_EMAIL,
        password=DEFAULT_ADMIN_PASSWORD,
        user_mode="users",
        ctf_theme=None,
    )

# Configure app permission system
with app.app_context():
    try:
        # This script is designed to run in production via 'pnpm populate-data'
        # where the plugin is properly located at /opt/CTFd/CTFd/plugins/ng
        from CTFd.plugins.ng.permissions.controllers.initial_admin_setup import initial_admin_setup  # type: ignore
        from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore
    except ImportError as e:
        print(f"Failed to import plugin modules: {e}")
        print("This script should be run via 'pnpm populate-data' from the project root.")
        raise

    # Get the admin user and create NG user extension
    ctfd_admin_user = Users.query.filter_by(name="admin").first()
    ng_admin_user = NgUser.query.filter_by(id=ctfd_admin_user.id).first()
    if not ng_admin_user:
        ng_admin_user = NgUser.create_user(user_id=ctfd_admin_user.id, commit=True)

    initial_admin_setup(admin_user=ng_admin_user)

# Insert sample data
with app.app_context():
    try:
        # This script is designed to run in production via 'pnpm populate-data'
        # where the plugin is properly located at /opt/CTFd/CTFd/plugins/ng
        from CTFd.plugins.ng.challenge.controllers.admin.import_challenge_from_yaml import (  # type: ignore
            import_challenge_from_yaml,  # type: ignore
        )
        from CTFd.plugins.ng.event.controllers.user.join_event_controller import join_event_controller  # type: ignore
        from CTFd.plugins.ng.event.models.Event import Event  # type: ignore
        from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore
    except ImportError as e:
        print(f"Failed to import plugin modules: {e}")
        print("This script should be run via 'pnpm populate-data' from the project root.")
        raise

    # Create sample events with different settings
    events = [
        Event.create_event(
            name="PC7 Teams Round 1",
            description="A CTF open to all teams",
            max_team_size=5,
            public=True,
            registration_open=True,
            commit=False,
        ),
        Event.create_event(
            name="Private Training Event",
            description="Internal training event for invited participants only",
            max_team_size=2,
            public=False,
            registration_open=True,
            commit=False,
        ),
        Event.create_event(
            name="PC7 Offensive Round 1",
            description="Individual challenges with no team collaboration",
            max_team_size=1,
            public=True,
            registration_open=True,
            commit=False,
        ),
        Event.create_event(
            name="Large Team Competition",
            description="Competition designed for large teams and organizations",
            max_team_size=8,
            public=False,
            registration_open=True,
            commit=False,
        ),
    ]

    # Commit the events
    db.session.commit()

    # Get the admin user and create NG user extension
    ctfd_admin_user = Users.query.filter_by(name="admin").first()
    ng_admin_user = NgUser.query.filter_by(id=ctfd_admin_user.id).first()
    if not ng_admin_user:
        ng_admin_user = NgUser.create_user(user_id=ctfd_admin_user.id, commit=True)

    # Create additional test user for team membership
    ctfd_test_user = Users(name="testuser", email="test@example.com", password="password", type="user")
    ctfd_test_user.verified = True

    ctfd_test_user_2 = Users(name="testuser2", email="test2@example.com", password="password", type="user")
    ctfd_test_user_2.verified = True

    db.session.add(ctfd_test_user)
    db.session.add(ctfd_test_user_2)
    db.session.commit()

    test_user = NgUser.create_user(user_id=ctfd_test_user.id, commit=True)
    test_user_2 = NgUser.create_user(user_id=ctfd_test_user_2.id, commit=True)

    # Register admin for first two events (Public CTF Championship and Private Training Event)
    admin_teams = []
    for i, event in enumerate(events[:2]):
        team_name = f"Admin Team {i + 1}" if i == 0 else "Elite Squad"
        team = join_event_controller(event=event, user=ng_admin_user, team_name=team_name)
        admin_teams.append(team)

    # Add test user as member to the first admin team
    first_team = admin_teams[0]
    join_event_controller(
        event=first_team.event,
        user=test_user,
        invite_code=first_team.invite_code,
    )

    # Create a sample team for test user2 in the first event
    first_event = events[0]
    test_team = join_event_controller(event=first_event, user=test_user_2, team_name="Test User2 Team")

    # Import sample challenge from default yaml
    with open(os.path.join(os.path.dirname(__file__), "../challenge/tests/yamls/default.yaml"), "rb") as f:
        yaml = f.read()

    for event in events:
        # Import the challenge for each event
        import_challenge_from_yaml(event=event, payload=yaml)

    print("Database reset and sample data creation completed!")
    print(f"Admin user created: {DEFAULT_ADMIN_EMAIL} ({DEFAULT_ADMIN_PASSWORD})")
    print(f"Created {len(events)} sample events:")
    for event in events:
        print(f"   - {event.name} (max_team_size: {event.max_team_size}, public: {event.public})")
    print(f"Admin user registered for {len(admin_teams)} events")
    print(f"Added test user to admin's first team: '{admin_teams[0].name if admin_teams else 'None'}'")
    print(f"Added test user2 to '{test_team.name}' in '{events[0].name}'")

    print("\n")
    # ANSI escape code for yellow background: \033[43m, reset: \033[0m
    print(f"Admin email: \033[43m{DEFAULT_ADMIN_EMAIL}\033[0m")
    print(f"Admin password: \033[43m{DEFAULT_ADMIN_PASSWORD}\033[0m")

if os.environ["LOAD_TEST"].lower() == "true":
    # Populate load testing data if LOAD_TEST environment variable is true
    populate_load_testing_data(app)