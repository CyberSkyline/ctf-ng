#!/usr/bin/env python3

import os

from CTFd import create_app
from CTFd.cache import cache
from CTFd.config import Config
from CTFd.models import db
from sqlalchemy_utils import create_database, database_exists, drop_database
from tests.helpers import setup_ctfd


if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

DEFAULT_ADMIN_EMAIL = "admin@examplectf.com"
DEFAULT_ADMIN_PASSWORD = "ctfng_password"

# Get the database URL from default config
database_url = Config.SQLALCHEMY_DATABASE_URI

# Drop and recreate database BEFORE creating the app
if database_exists(database_url):
    drop_database(database_url)

# Recreate the database
create_database(database_url, encoding="utf8mb4")

# Now create the app - it won't try to create tables in an existing database
app = create_app()

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

with app.app_context():
    # Import plugin modules after app initialization
    # This script is designed to run in production via 'pnpm populate-data'
    # where the plugin is properly located at /opt/CTFd/CTFd/plugins/ng
    try:
        from CTFd.plugins.ng.permissions.controllers.initial_admin_setup import initial_admin_setup  # type: ignore
        from CTFd.plugins.ng.user.models.User import User  # type: ignore
    except ImportError as e:
        print(f"Failed to import plugin modules: {e}")
        print("This script should be run via 'pnpm populate-data' from the project root.")
        raise

    admin_user = User.query.filter_by(id=1).first()
    if not admin_user:
        admin_user = User.create_user(1, commit=True)

    initial_admin_setup(admin_user=admin_user)

    print("\n")
    # ANSI escape code for yellow background: \033[43m, reset: \033[0m
    print(f"Admin email: \033[43m{DEFAULT_ADMIN_EMAIL}\033[0m")
    print(f"Admin password: \033[43m{DEFAULT_ADMIN_PASSWORD}\033[0m")
