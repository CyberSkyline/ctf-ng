from CTFd.models import db

from ...core.exceptions import ValidationError
from ...core.utils.validator import BaseValidator
from .enums import RoleEnum
from .Role import Role


class UserRole(db.Model):
    __tablename__ = "ng_user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("ng_roles.id"), nullable=False)

    user = db.relationship("User", back_populates="user_roles")
    role = db.relationship("Role", backref="user_roles")

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
        db.session.commit()
        return user_role

    @classmethod
    def get_user_roles(cls, user_id: int):
        """Retrieve all roles assigned to a specific user.

        Args:
            user_id (int): ID of the user

        Returns:
            list: List of Role instances assigned to the user
        """
        return [user_role.role for user_role in cls.query.filter_by(user_id=user_id).all()]

    @classmethod
    def assign_role_to_user_by_id(cls, user_id: int, role_id: int):
        """Assign a role to a user.

        Args:
            user_id (int): ID of the user
            role_id (int): ID of the role

        Returns:
            UserRole: The created user role instance
        """
        existing_user_role = cls.query.filter_by(user_id=user_id, role_id=role_id).first()
        if existing_user_role:
            return existing_user_role

        return cls.create_user_role(user_id, role_id)

    @classmethod
    def assign_role_to_user_by_name(cls, user_id: int, role_name: RoleEnum | str):
        name = role_name.value if isinstance(role_name, RoleEnum) else role_name
        role = Role.query.filter_by(name=name).first()

        if not role:
            raise ValidationError(f"Role '{name}' not found")

        return cls.assign_role_to_user_by_id(user_id, role.id)

    @classmethod
    def update_user_roles(cls, user_id: int, data):
        """Update roles for a specific user.

        Args:
            user_id (int): ID of the user to update roles for.
            data (dict): Dictionary containing role names to assign to the user.

        Returns:
            list: List of UserRole instances assigned to the user.
        """
        role_names = data.get("roles")
        if role_names is None:
            raise ValidationError("No role names provided")

        # Clear existing roles
        cls.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        # Assign new roles
        for role_name in role_names:
            cls.assign_role_to_user_by_name(user_id, role_name)

        # need to import User here to avoid circular imports
        from ...user.models.User import User

        user = User.find_by_id(user_id)
        return user

    @classmethod
    def get_user_role_by_id(cls, user_id: int):
        """Retrieve the user role for a specific user by user ID.

        Args:
            user_id (int): ID of the user

        Returns:
            UserRole: The user role instance or None if not found
        """
        return cls.query.filter_by(user_id=user_id).first()

    def serialize(self):
        """Serialize the UserRole instance to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "user": self.user.serialize() if self.user else None,
            "role": self.role.serialize() if self.role else None,
        }

    @classmethod
    def validate_user_role_update(cls, data):
        """Validate user role updates."""
        validator = BaseValidator()
        if data.get("roles") is None:
            validator.errors["roles"] = "No role names provided"
            raise ValidationError("No role names provided")

        for role in data["roles"]:
            validator.validate_enum({"roles": role}, "roles", RoleEnum, friendly_name="Role_name")

        result = validator.validate()
        if "roles" in result and not isinstance(result["roles"], list):
            result["roles"] = [result["roles"]]

        if "roles" not in result:
            # we passed roles = [], so the field doesn't get created in the result
            result["roles"] = []

        return result
