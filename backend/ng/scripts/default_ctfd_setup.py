#!/usr/bin/env python3

from CTFd import create_app
from tests.helpers import setup_ctfd
import os
from CTFd.plugins.ng.user.models.User import User
from CTFd.plugins.ng.permissions.models.Role import Role
from CTFd.plugins.ng.permissions.models.Permission import Permission
from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user
from CTFd.plugins.ng.permissions.controllers.create_role import create_role
from CTFd.plugins.ng.permissions.controllers.update_role import update_role

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
    
