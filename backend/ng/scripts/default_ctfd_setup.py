#!/usr/bin/env python3

import os

from CTFd import create_app
from CTFd.cache import cache
from CTFd.config import Config
from CTFd.models import db
from sqlalchemy_utils import create_database, database_exists, drop_database
from tests.helpers import setup_ctfd
import os
from CTFd.plugins.ng.user.models.User import User
from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user
from CTFd.plugins.ng.permissions.controllers.create_role import create_role
from CTFd.plugins.ng.permissions.controllers.create_permission import create_permission


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
create_database(database_url)

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
    admin_user = User.query.filter_by(id=1).first()
    if not admin_user:
         admin_user = User.create_user(1, commit=True)

    create_permission(
        name="CAN_EDIT_TEAMS",
        description="Can edit teams",
    )
    create_permission(
        name="CAN_EDIT_USER",
        description="Can edit users",
    )
    create_permission(
        name="CAN_MANAGE_SUPPORT_TICKETS",
        description="Can manage support tickets",
    )

    create_role(
        name="admin",
        permissions=[
            "CAN_EDIT_TEAMS",
            "CAN_EDIT_USER",
            "CAN_MANAGE_SUPPORT_TICKETS",
        ],
    )
    create_role(
        name="support",
        permissions=[
            "CAN_MANAGE_SUPPORT_TICKETS",
        ],
    )
    assign_role_to_user(admin_user.id, "admin")

    print("\n")
    # ANSI escape code for yellow background: \033[43m, reset: \033[0m
    print(f"Admin email: \033[43m{DEFAULT_ADMIN_EMAIL}\033[0m")
    print(f"Admin password: \033[43m{DEFAULT_ADMIN_PASSWORD}\033[0m")
