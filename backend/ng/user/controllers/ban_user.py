"""
Controller for banning and unbanning users
"""

from CTFd.cache import clear_user_session
from CTFd.models import db


def ban_user(user):
    """
    Ban a user, invalidating all their existing sessions
    """
    user.ctfd_user.banned = True
    clear_user_session(user_id=user.id)
    db.session.commit()


def unban_user(user):
    """
    Unban a user, allowing them to log in again
    """
    user.ctfd_user.banned = False
    db.session.commit()
