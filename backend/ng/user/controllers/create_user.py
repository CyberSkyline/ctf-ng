"""
Controller for creating new users
"""

from CTFd.models import Users, db

from ..models.User import User


def create_user(name: str, email: str, password: str) -> User:
    """
    Create a password-authenticated (expo) user and its NG extension
    """
    ctfd_user = Users(name=name, email=email, password=password, type="user")
    ctfd_user.verified = True

    db.session.add(ctfd_user)
    db.session.flush()

    ng_user = User.create_user(user_id=ctfd_user.id, commit=False)
    db.session.commit()

    return ng_user
