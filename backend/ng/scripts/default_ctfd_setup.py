#!/usr/bin/env python3

from CTFd import create_app
from tests.helpers import setup_ctfd
import os
from CTFd.plugins.ng.user.models.User import User
from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user
from CTFd.plugins.ng.permissions.controllers.create_role import create_role
from CTFd.plugins.ng.permissions.controllers.create_permission import create_permission

if "SCRIPT" not in os.environ:
    raise EnvironmentError('This should only be run from a script. DO NOT run this manually.')

app = create_app()

app = setup_ctfd(
        app,
        ctf_name="CTFd",
        ctf_description="CTF description",
        name="admin",
        email="admin@examplectf.com",
        password="password",
        user_mode="users",
        ctf_theme=None,
    )
with app.app_context():
    admin_user = User.query.filter_by(id=1).first()

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
    
