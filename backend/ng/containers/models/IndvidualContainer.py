from CTFd.models import db
from ... import config
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
        client = get_client(config.DOCKER_HOST)
        container_name = f'{user}-indv'
        exists = client.containers.get(container_name)
        if exists:
            return exists

        # Auto publish ports tagged in expose
        # For the indvidual container this means the vnc port
        ctr = client.containers.run(
            config.NOVNC_CONTAINER,
            name=container_name,
            detach=True,
            publish_all_ports=True,
        )

        indvidual_container = cls(
            user=user,
            hostip=config.DOCKER_HOST,
            dockerid=ctr.id,
        )

        db.session.add(indvidual_container)
        db.session.commit()
        return indvidual_container

    def connect_to_network(self, network):
        client = get_client(self.hostip)
        ctr = client.containers.get(self.dockerid)
        network.connect(ctr)

    def get_novnc_port(self):
        client = get_client(self.hostip)

        ctr_info = client.api.inspect_container(self.dockerid)
        ports = ctr_info['NetworkSettings']['Ports']

        host_port = ports[f'{config.NOVNC_PORT}/tcp']['HostPort']

        return host_port
