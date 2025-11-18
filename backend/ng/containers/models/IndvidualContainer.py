from CTFd.models import db
from CTFd.utils import get_app_config
import docker
from typing import TypedDict
from ... import config
from ..constants import DOCKER_RUNNING, DOCKER_BRIDGE
from ..utils.get_client import get_client
from .ContainerInstance import ContainerInstance

NOVNC_CONTAINER = get_app_config("NOVNC_CONTAINER")
NOVNC_PORT = get_app_config("NOVNC_PORT")

class SerializedIndvidualContainerInfo(TypedDict):
    id: int
    hostip: str
    dockerid: str
    user: int

class IndvidualContainer(db.Model):
    __tablename__ = "ng_indvidual_containers"
    id = db.Column(db.Integer, primary_key=True)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("ng_users.id"), nullable=False)

    def __repr__(self):
        return f"<IndvidualContainer {self.id}>"

    @classmethod
    def get_user_indvidual_container(cls, user_id: int):
        return cls.query.filter_by(user=user_id).first()

    @classmethod
    def create_indvidual_container(cls, user_id: int, commit: bool = True):
        db_exists = cls.query.filter_by(user=user_id).first()
        client = get_client(config.DOCKER_HOST)
        container_name = cls.render_container_name(user_id)

        if db_exists:
            try:
                ctr = client.get_running(db_exists.dockerid)
            except docker.errors.NotFound:
                ctr = cls.run_container(client, container_name)
                db_exists.dockerid = ctr.id
                db.session.commit()

            return db_exists

        try:
            exists = client.get_running(container_name)

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
            ctr = cls.run_container(client, container_name)

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

    @staticmethod
    def run_container(client, container_name):
        return client.containers.run(
            NOVNC_CONTAINER,
            name=container_name,
            detach=True,
            publish_all_ports=True,
        )


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

        network = client.get_network_by_name(network_name)

        network.connect(ctr)

    def get_novnc_port(self):
        client = get_client(self.hostip)

        ctr_info = client.api.inspect_container(self.dockerid)
        ports = ctr_info["NetworkSettings"]["Ports"]

        ## Port entries are an array of two one ipv4 one v6
        host_port = ports[f"{NOVNC_PORT}/tcp"][0]["HostPort"]

        return host_port

    def get_current_challenge(self) -> int | None:
        client = get_client(self.hostip)
        try:
            ctr_info = client.api.inspect_container(self.dockerid)
            current_challenge_network = None

            networks = ctr_info["NetworkSettings"]["Networks"]
            for network in networks:
                if network != DOCKER_BRIDGE:
                    current_challenge_network = network

            if not current_challenge_network:
                return None

            parsed_network = ContainerInstance.parse_network_name(current_challenge_network)

            return parsed_network["challenge_id"]

        except docker.errors.NotFound:
            # If the user workspace container doesn't exist, there is no current challenge
            return None

    def restart(self):
        client = get_client(self.hostip)
        try:
            ctr = client.containers.get(self.dockerid)
            ctr.restart()
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found please recycle") from exc

    def recycle(self):
        client = get_client(self.hostip)
        try:
            ctr = client.containers.get(self.dockerid)
            if ctr.status == DOCKER_RUNNING:
                ctr.kill()

            ctr.remove()

        except docker.errors.NotFound:
            pass

        finally:
            container_name = self.render_container_name(self.user)
            new_ctr = self.run_container(client, container_name)

            self.dockerid = new_ctr.id
            db.session.commit()


    def get_status(self) -> str:
        client = get_client(self.hostip)
        ctr = client.containers.get(self.dockerid)

        return ctr.status

    def serialize(self) -> SerializedIndvidualContainerInfo:
        data = {
            "id": self.id,
            "hostip": self.hostip,
            "dockerid": self.dockerid,
            "user": self.user,
        }

        return SerializedIndvidualContainerInfo(
            **data
        )

