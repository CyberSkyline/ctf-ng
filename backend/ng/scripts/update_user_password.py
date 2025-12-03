#!/usr/bin/env python3

import os
import sys

from CTFd import create_app
from CTFd.cache import cache
from CTFd.config import Config
from CTFd.models import Users, db

if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

if len(sys.argv) != 3:
    print("Usage: update_user_password.py <email_address> <password>")
    sys.exit(1)

email_address = sys.argv[1]
password = sys.argv[2]

database_url = Config.SQLALCHEMY_DATABASE_URI
app = create_app()

with app.app_context():
    # Clear cache
    cache.clear()

    user = Users.query.filter_by(email=email_address).first()
    if user is None:
        print(f"User with email {email_address} not found.")
        sys.exit(1)

    user.password = password

    db.session.commit()
    print(f"Password for {email_address} updated successfully.")
