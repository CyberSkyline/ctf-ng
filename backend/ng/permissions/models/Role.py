from CTFd.models import db
from sqlalchemy.ext.associationproxy import association_proxy

from ...core.exceptions import ValidationError
from ...core.utils.validator import BaseValidator
from .enums import PermissionEnum, RoleEnum
from .Permission import Permission
from .RolePermission import RolePermission


class Role(db.Model):
    __tablename__ = "ng_roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    role_permissions = db.relationship("RolePermission", backref="role", lazy="joined", cascade="all, delete-orphan")
    permissions = association_proxy(
        "role_permissions", "permission", creator=lambda permission: RolePermission(permission=permission)
    )

    def __repr__(self):
        return f"<Role {self.name}>"

    @classmethod
    def create_role(cls, name: RoleEnum, permissions: list[Permission] = None):
        """Create and persist a new role to the database.

        Args:
            name (str): Role name

        Returns:
            Role: The created role instance
        """
        role = cls.query.filter_by(name=name).first()
        if role:
            return role
        role = cls(name=name.value, permissions=permissions or [])
        db.session.add(role)
        db.session.commit()
        return role

    @classmethod
    def get_permissions(cls, role_id: int):
        """Retrieve permissions for a specific role.

        Args:
            role_id (int): ID of the role

        Returns:
            list: List of RolePermission instances for the role
        """
        return cls.query.get(role_id).permissions

    @classmethod
    def find_by_id(cls, role_id: int):
        """Find a role by its ID.

        Args:
            role_id (int): ID of the role

        Returns:
            Role: The role instance if found, else None
        """
        return cls.query.get(role_id)

    @classmethod
    def get_users_with_role(cls, role_name: RoleEnum):
        """Get all users who have a specific role.

        Args:
            role_name (RoleEnum): Name of the role to check

        Returns:
            list: List of User instances with the specified permission
        """
        # need to import UserRole and User here to avoid circular imports
        from ...user.models.User import User
        from .UserRole import UserRole

        return User.query.join(User.user_roles).join(UserRole.role).filter(Role.name == role_name.value).all()

    @classmethod
    def get_role_by_name(cls, name: RoleEnum):
        """Retrieve a role by its name.

        Args:
            name (RoleEnum): Name of the role

        Returns:
            Role: The role instance if found, else None
        """
        return cls.query.filter_by(name=name).first()

    def serialize(self, include_admin_fields=False):
        """Serialize a Role instance to a dictionary.

        Returns:
            dict: Serialized role data
        """
        return (
            {
                "id": self.id,
                "name": self.name,
                "permissions": [permission.serialize() for permission in self.permissions],
            }
            if self
            else None
        )

    @classmethod
    def validate_role_update(cls, data):
        """Validate role updates."""
        validator = BaseValidator()

        if not any(data.get(field) is not None for field in ["name", "description", "permissions"]):
            raise ValidationError("At least one field must be provided for update")

        if "name" in data:
            validator.validate_string(
                data,
                "name",
                required=False,
                friendly_name="Role name",
            )
        if "description" in data:
            validator.validate_string(
                data,
                "description",
                required=False,
                friendly_name="Role description",
            )
        if "permissions" in data:
            for permission in data["permissions"]:
                validator.validate_enum(
                    {"permissions": permission},
                    "permissions",
                    PermissionEnum,
                    required=False,
                    friendly_name="Permission_name",
                )

        return validator.validate()

    @classmethod
    def update_role(cls, role, data):
        """
        Update the details of a specific role

        Args:
            role_id (int): The ID of the role to update.
            data (dict): The new data for the role, including name and permissions.

        Returns:
            dict: The updated role details or an error message.
        """

        role.name = data.get("name", role.name)
        permission_names = data.get("permissions", [])
        permissions = []
        if permission_names:
            for name in permission_names:
                permissions.append(Permission.get_permission_by_name(name))
        role.permissions = permissions
        db.session.commit()

        return role
