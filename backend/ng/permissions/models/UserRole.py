from CTFD.models import db

class UserRole(db.Model):
    __tablename__ = "ng_user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("ng_roles.id"), nullable=False)

    

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"

    @classmethod
    def create_user_role(cls, user_id: int, role_id: int):
        """Create and persist a new user role to the database.

        Args:
            user_id (int): ID of the user
            role_id (int): ID of the role

        Returns:
            UserRole: The created user role instance
        """
        user_role = cls(user_id=user_id, role_id=role_id)
        db.session.add(user_role)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"UserRole with user_id '{user_id}' and role_id '{role_id}' already exists.")
        return user_role
    
    @classmethod
    def get_user_role(cls, user_id: int):
        """Retrieve the role of a specific user.

        Args:
            user_id (int): ID of the user

        Returns:
            UserRole: The user role entry for the user
        """
        return cls.query.filter_by(user_id=user_id).first()

