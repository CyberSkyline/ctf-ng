#!/usr/bin/env python3
import sys
from contextlib import redirect_stdout

original_stdout = sys.stdout

with redirect_stdout(sys.stderr):
    from CTFd import create_app, CTFdFlask
    from CTFd.models import Users, db
    from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore
    from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user # type: ignore
    from CTFd.plugins.ng.permissions.models.enums import RoleEnum # type: ignore
    import secrets
    import json


    # Now create the app - it won't try to create tables in an existing database
    app: CTFdFlask = create_app()

    with app.app_context():
        # Create load testing users
        users = {"users": [], "admins": []}

        for i in range(0, 500):
            app.logger.info(f"Creating load testing user {i}")
            name = f"Load Testing User {i}"
            email = f"{secrets.token_urlsafe(30)}@example.com"
            password = secrets.token_urlsafe(30)
            users['users'].append({"name": name, "email": email, "password": password})
            user = Users(name=name, email=email, password=password, type="user")
            user.verified = True
            db.session.add(user)
            db.session.commit()

            NgUser.create_user(user_id=user.id, commit=True)

        for i in range(0, 5):
            app.logger.info(f"Creating load testing admin {i}")
            name = f"Load Testing Admin {i}"
            email = f"{secrets.token_urlsafe(30)}@example.com"
            password = secrets.token_urlsafe(30)
            users['admins'].append({"name": name, "email": email, "password": password})
            admin_user = Users(name=name, email=email, password=password, type="user")
            admin_user.verified = True
            db.session.add(admin_user)
            db.session.commit()

            NgUser.create_user(user_id=admin_user.id, commit=True)
            assign_role_to_user(admin_user.id, RoleEnum.ADMIN)

        # Output the created users to a JSON file for load testing purposes
        app.logger.info("Load testing users created successfully. Outputting to users.json")
        print(json.dumps(users, indent=4), file=original_stdout)
