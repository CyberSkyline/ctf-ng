from CTFd.models import db
from ..utils.get_client import get_client

class IndvidualContainer(db.Model):
    __tablename__ = 'ng_indvidual_container'
    id = db.Column(db.Integer, primary_key=True)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('ng_user.id'), nullable=False)

    def __repr__(self):
        return f'<IndvidualContainer {self.id}>'

    @classmethod
    def create_indvidual_container(cls, user):
        client = get_client('10.100.20.246')
        container_name = f'{user}-indv'
        exists = client.containers.get(container_name)
        if (exists):
            return exists

        ctr = client.containers.run('vnc-image', name=container_name, detach=True)

        indvidual_container = cls(
            user=user,
            hostip='10.100.20.246',
            dockerid=ctr.id,
        )

        db.session.add(indvidual_container)
        db.session.commit()
        return indvidual_container

    def connect_to_network(self, network):
        return

    def get_novnc_port(self):
        return
