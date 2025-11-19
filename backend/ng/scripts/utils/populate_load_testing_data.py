
from CTFd import CTFdFlask
from CTFd.models import Users, db
from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore
from CTFd.plugins.ng.permissions.controllers.assign_role_to_user import assign_role_to_user # type: ignore
from CTFd.plugins.ng.permissions.models.enums import RoleEnum # type: ignore

def populate_load_testing_data(app: CTFdFlask):
    with app.app_context():
        app.logger.info("Populating load testing data...")
        # Create sample users
        for i in range(0, 500):
            app.logger.info(f"Creating load testing user {i}")
            user = Users(name=f"Load Testing User {i}", email=f"loadtesting{i}@example.com", password=f"loadtesting{i}", type="user")
            user.verified = True
            db.session.add(user)
            db.session.commit()

            NgUser.create_user(user_id=user.id, commit=True)

        for i in range(0, 5):
            app.logger.info(f"Creating load testing admin user {i}")
            admin_user = Users(name=f"Load Testing Admin {i}", email=f"loadtesting{i}admin@example.com", password=f"loadtesting{i}admin", type="user")
            admin_user.verified = True
            db.session.add(admin_user)
            db.session.commit()

            NgUser.create_user(user_id=admin_user.id, commit=True)
            assign_role_to_user(admin_user.id, RoleEnum.ADMIN)

        app.logger.info("Load testing data population complete.")
