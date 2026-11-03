from CTFd.models import db
from .enums import PermissionEnum

class Permission(db.Model):
    __tablename__ = "ng_permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    roles = db.relationship("RolePermission", backref="permission")

    def __repr__(self):
        return f"<Permission {self.name}>"

    @classmethod
    def create_permission(cls, name: PermissionEnum, description: str = None):
        """Create and persist a new permission to the database.

        Args:
            name (str): Permission name
            description (str): Optional description of the permission

        Returns:
            Permission: The created permission instance
        """
        existing_permission = cls.query.filter_by(name=name.value).first()
        if existing_permission:
            return existing_permission
        permission = cls(name=name.value, description=description)
        db.session.add(permission)
        db.session.commit()
        return permission


    @classmethod
    def get_permission_by_id(cls, permission_id: int):
        """Retrieve a permission by its ID.

        Args:
            permission_id (int): ID of the permission

        Returns:
            Permission: The permission instance if found, else None
        """
        return cls.query.get(permission_id)


    @classmethod
    def get_permission_by_name(cls, name: PermissionEnum):
        """Retrieve a permission by its name.

        Args:
            name (str): Name of the permission

        Returns:
            Permission: The permission instance if found, else None
        """

        return cls.query.filter_by(name=name.value).first()

    @classmethod
    def get_permissions_for_user(cls, user_id: int):
        """Retrieve every permission granted across a user's roles, in one query.

        Args:
            user_id (int): ID of the user

        Returns:
            list[Permission]: Distinct permissions granted to the user
        """
        # LAZY-IMPORT
        from .RolePermission import RolePermission
        from .UserRole import UserRole

        return (cls.query
            .join(RolePermission, RolePermission.permission_id == cls.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .filter(UserRole.user_id == user_id)
            .distinct()
            .all()
        )

    def serialize(self):
        """Serialize a Permission instance to a dictionary.

        Returns:
            dict: Serialized permission data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }