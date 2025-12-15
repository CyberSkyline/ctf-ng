#!/usr/bin/env python3

import os
import sys

from CTFd import create_app
from CTFd.cache import cache
from CTFd.config import Config
from CTFd.models import Users, db

if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

email_address = sys.argv[1]
password = sys.argv[2]

database_url = Config.SQLALCHEMY_DATABASE_URI
app = create_app()

with app.app_context():
    from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user
    from CTFd.plugins.ng.permissions.models.enums import RoleEnum
    from CTFd.plugins.ng.user.models.User import User as NgUser

    cache.clear()

    user = Users.query.filter_by(email=email_address).first()
    if user is not None:
        print(f"User with email {email_address} already exists.")
        sys.exit(1)

    new_user = Users(name="new user", email=email_address, password=password, type="user")
    new_user.verified = True

    db.session.add(new_user)
    db.session.commit()

    ng_user = NgUser.create_user(user_id=new_user.id, commit=True)

    assign_role_to_user(ng_user.id, RoleEnum.ADMIN)

    print(f"New admin user, {email_address}, has been created.")
