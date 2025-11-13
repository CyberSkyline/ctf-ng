
from CTFd import CTFdFlask
from CTFd.models import Users, db

def populate_load_testing_data(app: CTFdFlask):
    with app.app_context():
        # Create sample users
        for i in range(0, 500):
            user = Users(name=f"Load Testing User {i}", email=f"loadtesting{i}@example.com", password=f"loadtesting{i}", type="user")
            user.verified = True
            db.session.add(user)

        db.session.commit()
