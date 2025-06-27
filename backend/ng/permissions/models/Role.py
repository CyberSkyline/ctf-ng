from CTFd.models import db


class Role(db.model):
    __tablename__ = "ng_roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def repr(self):
        return f"<Role {self.name}>"

    @classmethod
    def create_role(cls, name: str):
        """Create and persist a new role to the database.

        Args:
            name (str): Role name

        Returns:
            Role: The created role instance
        """
        role = cls(name=name)
        db.session.add(role)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Role with name '{name}' already exists.")
        return role