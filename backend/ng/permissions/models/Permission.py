from CTFD.models import db

class Permission(db.Model):
    __tablename__ = "ng_permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

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
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Permission with name '{name}' already exists.")
        return permission