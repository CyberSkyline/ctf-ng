#!/usr/bin/env python3

import argparse
import csv
import os
import sys

from CTFd import create_app
from CTFd.models import Users, db

if "SCRIPT" not in os.environ:
    raise OSError("This should only be run from a script. DO NOT run this manually.")

parser = argparse.ArgumentParser(description="Create a new user or batch of users.")
parser.add_argument("email", nargs="?", help="Email address for the new user")
parser.add_argument("password", nargs="?", help="Password for the new user")
parser.add_argument("--admin", action="store_true", help="Grant the user (or all CSV users) admin role")
parser.add_argument("--name", default="new user", help="Display name for the new user (default: 'new user')")
parser.add_argument("--csv", dest="csv_path", help="Path to a CSV file with columns: email, password, name")
args = parser.parse_args()

if args.csv_path and (args.email or args.password):
    print("Error: --csv cannot be combined with positional email/password arguments.")
    sys.exit(1)

if not args.csv_path and not (args.email and args.password):
    print("Error: provide either a --csv file or both email and password arguments.")
    sys.exit(1)

app = create_app()

with app.app_context():
    from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user
    from CTFd.plugins.ng.permissions.models.enums import RoleEnum
    from CTFd.plugins.ng.user.models.User import User as NgUser

    def create_one(email, password, name):
        user = Users.query.filter_by(email=email).first()
        if user is not None:
            print(f"Skipped: user with email {email} already exists.")
            return False

        new_user = Users(name=name, email=email, password=password, type="user")
        new_user.verified = True
        db.session.add(new_user)
        db.session.commit()

        ng_user = NgUser.create_user(user_id=new_user.id, commit=True)

        if args.admin:
            assign_role_to_user(ng_user.id, RoleEnum.ADMIN)
            print(f"New admin user '{name}' ({email}) has been created.")
        else:
            print(f"New user '{name}' ({email}) has been created.")
        return True

    if args.csv_path:
        if not os.path.exists(args.csv_path):
            print(f"Error: CSV file not found: {args.csv_path}")
            sys.exit(1)

        created = 0
        skipped = 0
        with open(args.csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("email", "").strip()
                password = row.get("password", "").strip()
                name = row.get("name", "").strip() or "new user"
                if not email or not password:
                    print(f"Skipped row with missing email or password: {row}")
                    skipped += 1
                    continue
                if create_one(email, password, name):
                    created += 1
                else:
                    skipped += 1

        print(f"\nDone: {created} created, {skipped} skipped.")
    else:
        create_one(args.email, args.password, args.name)
