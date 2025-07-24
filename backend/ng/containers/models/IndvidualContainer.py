from CTFd.models import db
import docker
from ... import config
from ..constants import DOCKER_RUNNING, DOCKER_BRIDGE
from ..utils.get_client import get_client

class IndvidualContainer(db.Model):
    __tablename__ = "ng_indvidual_containers"
    id = db.Column(db.Integer, primary_key=True)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False)

    def __repr__(self):
        return f"<IndvidualContainer {self.id}>"

    @classmethod
    def create_indvidual_container(cls, user_id: int, commit: bool = True):
        db_exists = cls.query.filter_by(user=user_id).first()
        client = get_client(config.DOCKER_HOST)
        if db_exists:
            ctr = client.containers.get(db_exists.dockerid)
            if ctr.status != DOCKER_RUNNING:
                ctr.start()

            return db_exists

        container_name = cls.render_container_name(user_id)
        try:
            exists = client.containers.get(container_name)
            if exists.status != DOCKER_RUNNING:
                exists.start()

            indv = cls(
                user=user_id,
                hostip=config.DOCKER_HOST,
                dockerid=exists.id,
            )
            db.session.add(indv)
            if commit:
                db.session.commit()
            return indv

        except docker.errors.NotFound:

            # Auto publish ports tagged in expose
            # For the indvidual container this means the vnc port
            ctr = client.containers.run(
                config.NOVNC_CONTAINER,
                name=container_name,
                detach=True,
                publish_all_ports=True,
            )

            indvidual_container = cls(
                user=user_id,
                hostip=config.DOCKER_HOST,
                dockerid=ctr.id,
            )

            db.session.add(indvidual_container)
            if commit:
                db.session.commit()
            return indvidual_container

    @staticmethod
    def render_container_name(user_id) -> str:
        return f"{user_id}-indv"

    def disconnect_from_networks(self):
        # Disconnect your indvidual container from challenge networks
        # Bridge needs to stay for vnc
        client = get_client(self.hostip)
        inspect_results = client.api.inspect_container(self.dockerid)
        networks = inspect_results["NetworkSettings"]["Networks"]
        for network in networks:
            if network != DOCKER_BRIDGE:
                fetched_network = client.networks.get(networks[network]["NetworkID"])
                fetched_network.disconnect(self.dockerid)

    def connect_to_network(self, network_name: str):
        client = get_client(self.hostip)
        ctr = client.containers.get(self.dockerid)

        network = client.networks.list(names=[network_name])[0]

        network.connect(ctr)

    def get_novnc_port(self):
        client = get_client(self.hostip)

        ctr_info = client.api.inspect_container(self.dockerid)
        ports = ctr_info["NetworkSettings"]["Ports"]

        ## Port entries are an array of two one ipv4 one v6
        host_port = ports[f"{config.NOVNC_PORT}/tcp"][0]["HostPort"]

        return host_port
