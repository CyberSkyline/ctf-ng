from CTFd.models import db

class ContainerBlueprint(db.Model):
    __tablename__ = 'ng_container_blueprint'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255))
    hostname = db.Column(db.String(255))
    stdin_open = db.Column(db.Boolean, nullable=True)
    tty = db.Column(db.Boolean, nullable=True)
    command = db.Column(db.PickleType, nullable=True)
    entrypoint = db.Column(db.PickleType, nullable=True)
    environment = db.Column(db.PickleType, nullable=True)
    networks = db.Column(db.PickleType, nullable=True)
    cap_add = db.Column(db.PickleType, nullable=True)
    mem_limit = db.Column(db.String(255), nullable=True)
    memswap_limit = db.Column(db.String(255), nullable=True)
    cpus = db.Column(db.Numeric, nullable=True)
    user = db.Column(db.String(255), nullable=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('ng_challenge.id'), nullable=False, index=True)

    def __repr__(self):
        return f'<ContainerBlueprint {self.id}>'

    @classmethod
    def create_container_blueprint(cls, commit=True, **kwargs):
        try:
            blueprint = cls(**kwargs)
            db.session.add(blueprint)
            if commit:
                db.session.commit()
            return blueprint
        except Exception as e:
            db.session.rollback()
            raise e
