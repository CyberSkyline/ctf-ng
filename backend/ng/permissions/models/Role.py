from CTFd.models import db
from sqlalchemy.ext.associationproxy import association_proxy
from .RolePermission import RolePermission
from .Permission import Permission
from .enums import RoleEnum

class Role(db.Model):
    __tablename__ = "ng_roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    role_permissions = db.relationship("RolePermission", backref="role", lazy="joined", cascade="all, delete-orphan")
    permissions = association_proxy("role_permissions","permission",creator=lambda permission: RolePermission(permission=permission))

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
    def get_users_with_role(cls, role_name: RoleEnum):
        """Get all users who have a specific role.

        Args:
            role_name (RoleEnum): Name of the role to check

        Returns:
            list: List of User instances with the specified permission
        """
        #need to import UserRole and User here to avoid circular imports
        from .UserRole import UserRole
        from ...user.models.User import User
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



    def serialize(self):
        """Serialize a Role instance to a dictionary.

        Returns:
            dict: Serialized role data
        """
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [permission.serialize() for permission in self.permissions]
        } if self else None