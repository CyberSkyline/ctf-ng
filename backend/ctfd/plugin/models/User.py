from CTFd.models import db

"""
"""

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    
    teams = db.relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")