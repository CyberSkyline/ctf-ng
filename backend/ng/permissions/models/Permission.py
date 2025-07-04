from CTFd.models import db
from .RolePermission import RolePermission

class Permission(db.Model):
    __tablename__ = "ng_permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    roles = db.relationship("RolePermission", backref="permission", lazy="joined")

    def __repr__(self):
        return f"<Permission {self.name}>"

    @classmethod
    def create_permission(cls, name: str, description: str = None):
        """Create and persist a new permission to the database.

        Args:
            name (str): Permission name
            description (str): Optional description of the permission

        Returns:
            Permission: The created permission instance
        """
        permission = cls(name=name, description=description)
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
    def get_permission_by_name(cls, name: str):
        """Retrieve a permission by its name.

        Args:
            name (str): Name of the permission

        Returns:
            Permission: The permission instance if found, else None
        """
        return cls.query.filter_by(name=name).first()

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