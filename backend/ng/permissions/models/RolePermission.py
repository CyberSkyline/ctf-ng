from CTFD.models import db

class RolePermission(db.Model):
    __tablename__ = "ng_role_permissions"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("ng_roles.id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("ng_permissions.id"), nullable=False)
    role = db.relationship("Role", backref="permissions", lazy="joined")

    def __repr__(self):
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"


    @classmethod
    def create_role_permission(cls, role_id: int, permission_id: int):
        """Create and persist a new role permission to the database.

        Args:
            role_id (int): ID of the role
            permission_id (int): ID of the permission

        Returns:
            RolePermission: The created role permission instance
        """
        role_permission = cls(role_id=role_id, permission_id=permission_id)
        db.session.add(role_permission)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"RolePermission with role_id '{role_id}' and permission_id '{permission_id}' already exists.")
        return role_permission

    @classmethod
    def get_permissions_by_role(cls, role_id: int):
        """Retrieve permissions for a specific role.

        Args:
            role_id (int): ID of the role

        Returns:
            list: List of RolePermission instances for the role
        """
        return cls.query.filter_by(role_id=role_id).all()