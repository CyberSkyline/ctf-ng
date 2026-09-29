from CTFd.models import db
from CTFd.utils import get_app_config
import docker
import redis_lock
from typing import TypedDict
from ..constants import DOCKER_RUNNING, DOCKER_BRIDGE, DOCKER_MEM_REGEX
from ..utils.get_client import get_client
from ..utils.scheduler import get_client_ip_round_robin
from ...core import BusinessLogicError
from .ContainerInstance import ContainerInstance
from ..utils.redis import get_redis_client

LOCK_EXPIRE_SECONDS = 5*60

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
    def get_indvidual_container_by_dockerid(cls, docker_id: str):
        return cls.query.filter_by(dockerid=docker_id).first()

    @classmethod
    def create_indvidual_container(cls, user_id: int, commit: bool = True):
        redis_client = get_redis_client(3)

        db_exists = cls.query.filter_by(user=user_id).first()
        # DOCKER_HOST = get_app_config("DOCKER_HOST")
        # TODO db_exists should pull client from hostip
        DOCKER_HOST = get_client_ip_round_robin()
        client = get_client(DOCKER_HOST)
        container_name = cls.render_container_name(user_id)

        if db_exists:
            try:
                client = get_client(db_exists.hostip)
                ctr = client.get_running(db_exists.dockerid)
            except docker.errors.NotFound:
                lock = redis_lock.Lock(redis_client, cls.render_lock_key(user_id), expire=LOCK_EXPIRE_SECONDS)
                if lock.acquire(blocking=False):
                    ctr = cls.run_container(client, container_name)
                    db_exists.dockerid = ctr.id
                    db.session.commit()
                    lock.release()
                else:
                    raise BusinessLogicError("Workspace is already being started/reset") from None

            return db_exists

        try:
            exists = client.get_running(container_name)

            indv = cls(
                user=user_id,
                hostip=DOCKER_HOST,
                dockerid=exists.id,
            )
            db.session.add(indv)
            if commit:
                db.session.commit()
            return indv

        except docker.errors.NotFound:
            lock = redis_lock.Lock(redis_client, cls.render_lock_key(user_id), expire=LOCK_EXPIRE_SECONDS)
            if lock.acquire(blocking=False):
                ctr = cls.run_container(client, container_name)

                indvidual_container = cls(
                    user=user_id,
                    hostip=DOCKER_HOST,
                    dockerid=ctr.id,
                )

                db.session.add(indvidual_container)
                if commit:
                    db.session.commit()
                lock.release()
            else:
                raise BusinessLogicError("Workspace is already being started/reset") from None

            return indvidual_container

    @staticmethod
    def render_container_name(user_id) -> str:
        return f"{user_id}-indv"

    @staticmethod
    def render_lock_key(user_id) -> str:
        return f"{user_id}-vnc-lock"

    @staticmethod
    def run_container(client, container_name, lock=None):
        NOVNC_CONTAINER = get_app_config("NOVNC_CONTAINER")

        NOVNC_RAM = get_app_config("NOVNC_RAM", "4g")

        parsed_ram = DOCKER_MEM_REGEX.match(NOVNC_RAM)
        ram_number = int(parsed_ram.group(1))
        ram_postfix = parsed_ram.group(2)

        swap_mem = f"{round(ram_number * 1.5)}{ram_postfix}"
        mem_resv = f"{round(ram_number * 0.8)}{ram_postfix}"


        ulimit = docker.types.Ulimit(name="nofile", soft=10000, hard=20000)

        net = client.get_network_by_name(container_name)

        if not net:
            net = client.networks.create(name=container_name, driver="bridge")


        # I am not setting a kernel memory limit
        # As you it is deprecated
        # See https://github.com/torvalds/linux/commit/0158115f702b0ba208ab0b5adf44cae99b3ebcc7
        return client.containers.run(
            NOVNC_CONTAINER,
            name=container_name,
            detach=True,
            publish_all_ports=True,
            cap_add=[
                "NET_ADMIN",
                "SYS_PTRACE",
            ],
            mem_limit=NOVNC_RAM,
            mem_reservation=mem_resv,
            memswap_limit=swap_mem,
            cpu_period=200000,
            cpu_quota=100000,
            pids_limit=5000,
            ulimits=[ulimit],
            network=net.name,
        )


    def disconnect_from_networks(self):
        # Disconnect your indvidual container from challenge networks
        # Bridge needs to stay for vnc
        user_bridge_name = self.render_container_name(self.user)
        client = get_client(self.hostip)
        inspect_results = client.api.inspect_container(self.dockerid)
        networks = inspect_results["NetworkSettings"]["Networks"]
        for network in networks:
            if network != DOCKER_BRIDGE and network != user_bridge_name:
                fetched_network = client.networks.get(networks[network]["NetworkID"])
                fetched_network.disconnect(self.dockerid)

    def connect_to_network(self, network_name: str):
        client = get_client(self.hostip)
        ctr = client.containers.get(self.dockerid)

        network = client.get_network_by_name(network_name)

        network.connect(ctr)

    def get_novnc_port(self):
        NOVNC_PORT = get_app_config("NOVNC_PORT")

        client = get_client(self.hostip)

        ctr_info = client.api.inspect_container(self.dockerid)
        ports = ctr_info["NetworkSettings"]["Ports"]

        ## Port entries are an array of two one ipv4 one v6
        host_port = ports[f"{NOVNC_PORT}/tcp"][0]["HostPort"]

        return host_port

    def get_current_challenge(self) -> int | None:
        client = get_client(self.hostip)
        user_bridge_name = self.render_container_name(self.user)

        try:
            ctr_info = client.api.inspect_container(self.dockerid)
            current_challenge_network = None

            networks = ctr_info["NetworkSettings"]["Networks"]
            for network in networks:
                if (network != DOCKER_BRIDGE) and (network != user_bridge_name):
                    current_challenge_network = network

            if not current_challenge_network:
                return None

            parsed_network = ContainerInstance.parse_network_name(current_challenge_network)

            return parsed_network["challenge_id"]

        except docker.errors.NotFound:
            # If the user workspace container doesn't exist, there is no current challenge
            return None

    def restart(self):
        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, self.render_lock_key(self.user), expire=LOCK_EXPIRE_SECONDS)
        if lock.acquire(blocking=False):
            client = get_client(self.hostip)
            try:
                ctr = client.containers.get(self.dockerid)
                ctr.restart()
            except docker.errors.NotFound as exc:
                raise ValueError("Container not found please recycle") from exc
            finally:
                lock.release()
        else:
            raise BusinessLogicError("Workspace is already being started/reset")

    def recycle(self):
        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, self.render_lock_key(self.user), expire=LOCK_EXPIRE_SECONDS)
        if lock.acquire(blocking=False):
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
                lock.release()
        else:
            raise BusinessLogicError("Workspace is already being started/reset")

    def stop(self):
        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, self.render_lock_key(self.user), expire=LOCK_EXPIRE_SECONDS)
        if lock.acquire(blocking=False):
            client = get_client(self.hostip)
            try:
                ctr = client.containers.get(self.dockerid)
                if ctr.status == DOCKER_RUNNING:
                    ctr.stop(timeout=5)
            except docker.errors.NotFound:
                pass
            lock.release()
        else:
            raise BusinessLogicError("Workspace is already being started/reset")

    def delete(self, commit=True):
        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, self.render_lock_key(self.user), expire=LOCK_EXPIRE_SECONDS)
        if lock.acquire(blocking=False):
            client = get_client(self.hostip)
            try:
                ctr = client.containers.get(self.dockerid)
                ctr.remove(force=True)
            except docker.errors.NotFound:
                try:
                    ctr = client.containers.get(self.render_container_name(self.user))
                    ctr.remove(force=True)
                except docker.errors.NotFound:
                    pass
            db.session.delete(self)
            if commit:
                db.session.commit()
            lock.release()
        else:
            raise BusinessLogicError("Workspace is already being started/reset")

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
