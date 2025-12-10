#!/usr/bin/env python3
import sys
from contextlib import redirect_stdout

original_stdout = sys.stdout

with redirect_stdout(sys.stderr):
    from CTFd import create_app, CTFdFlask
    from CTFd.models import Users, db
    from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore
    from CTFd.plugins.ng.event.models.Event import Event  # type: ignore
    from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user # type: ignore
    from CTFd.plugins.ng.challenge.controllers.admin.import_challenge_from_yaml import (  # type: ignore
        import_challenge_from_yaml,  # type: ignore
    )
    from CTFd.plugins.ng.permissions.models.enums import RoleEnum # type: ignore
    import secrets
    import json
    import os


    # Now create the app - it won't try to create tables in an existing database
    app: CTFdFlask = create_app()

    with app.app_context():

        event = Event.create_event(
            name="CTFd Load Testing Event",
            description="A CTF open to all teams",
            max_team_size=1,
            public=True,
            registration_open=True,
            commit=True,
        )

            # Import sample challenge from default yaml
        with open(os.path.join(os.path.dirname(__file__), "../challenge/tests/yamls/default.yaml"), "rb") as f:
            yaml = f.read()

        challenge = import_challenge_from_yaml(event=event, payload=yaml)

        # Create load testing users
        users = {
            "event_id": event.id,
            "challenge_id": challenge.id,
            "question_id": challenge.questions[0].id if challenge.questions else None,
            "users": [], 
            "admins": []
        }

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
