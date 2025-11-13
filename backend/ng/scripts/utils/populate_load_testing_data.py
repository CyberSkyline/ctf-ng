
from CTFd import CTFdFlask
from CTFd.models import Users, db
from CTFd.plugins.ng.user.models.User import User as NgUser  # type: ignore

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

        app.logger.info("Load testing data population complete.")
