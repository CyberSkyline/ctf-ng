from CTFd.models import db
import docker
import io
import re
import redis_lock
from sqlalchemy import func, select
from sqlalchemy.orm import Mapped
from typing import TypedDict
import logging

from ..utils.get_client import get_client
from ..utils.Client import Client
from CTFd.utils import get_app_config
from .. constants import DOCKER_RUNNING, DOCKER_BRIDGE, DOCKER_MEM_REGEX, DOCKER_QUOTA_CONST
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ...team.models.Team import Team
from ...core import BusinessLogicError
from ..utils.redis import get_redis_client

logger = logging.getLogger(__name__)

NET_ERR_REGEX = re.compile("(?:endpoint.*already exists in)|(?:already attached to network)")

class SerializedInstanceStats(TypedDict):
    id: int
    name: str
    image: str
    docker_id: str
    status: str

class SerializedContainerInstance(TypedDict):
    id: int
    blueprint: int
    team_id: int
    hostip: str
    dockerid: str

class ContainerInstance(db.Model):
    __tablename__ = "ng_container_instances"
    id = db.Column(db.Integer, primary_key=True)
    blueprint = db.Column(db.Integer, db.ForeignKey("ng_container_blueprints.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid: Mapped[str] = db.Column(db.String(255), nullable=False)

    team = db.relationship("Team")

    def __repr__(self):
        return f"<ContainerInstance {self.id}>"

    @classmethod
    def find_by_id(cls, instance_id: int):
        return cls.query.filter_by(id=instance_id).first()

    @classmethod
    def create_container_instance(cls, blueprint: int, team: Team, commit: bool = True):
        blueprint_obj = ContainerBlueprint.query.filter_by(id=blueprint).first()

        db_exists = cls.query.filter_by(blueprint=blueprint, team_id=team.id).first()

        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)

        if db_exists:
            try:
                ctr = client.get_running(db_exists.dockerid)

            ## Container Needs created
            except docker.errors.NotFound:
                ctr = cls.run_container(client, team, blueprint_obj)
                cls.connect_networks(client, team, blueprint_obj, ctr)

                db_exists.dockerid = ctr.id
                db.session.commit()

            ## Container won't start
            ## Edge case of entry point getting nuked or something
            except docker.errors.APIError:
                tmp_ctr = client.containers.get(db_exists.dockerid)
                tmp_ctr.remove(force=True)

                ctr = cls.run_container(client, team, blueprint_obj)
                cls.connect_networks(client, team, blueprint_obj, ctr)

                db_exists.dockerid = ctr.id
                db.session.commit()

            return db_exists

        ctr = None
        try:
            ctr = client.get_running(
                cls.render_container_name(team.id, blueprint_obj.name, blueprint_obj.challenge_id)
            )

        ## Container Needs created
        except docker.errors.NotFound:
            ctr = cls.run_container(client, team, blueprint_obj)

        ## Container won't start
        ## Edge case of entry point getting nuked or something
        except docker.errors.APIError:
            tmp_ctr = client.containers.get(
                cls.render_container_name(team.id, blueprint_obj.name, blueprint_obj.challenge_id)
             )
            tmp_ctr.remove(force=True)

            ctr = cls.run_container(client, team, blueprint_obj)

        try:
            cls.connect_networks(client, team, blueprint_obj, ctr)

        except Exception as err:
            # Remove on network fail
            ctr.remove(force=True)
            raise err


        container_instance = cls(
            blueprint=blueprint,
            team_id=team.id,
            hostip=DOCKER_HOST,
            dockerid=ctr.id,
        )

        db.session.add(container_instance)
        if commit:
            db.session.commit()
        return container_instance

    @staticmethod
    def render_container_name(team_id: int, servicename: str, challenge_id: int) -> str:
        return f"{team_id}-{servicename}-{challenge_id}"

    @staticmethod
    def render_network_name(team_id: int, network_name: str, challenge_id: int) -> str:
        return f"{network_name}-{team_id}-{challenge_id}"

    @staticmethod
    def render_lock_key(team_id: int, challenge_id: int) -> str:
        return f"{team_id}-{challenge_id}-chall-lock"

    @staticmethod
    def parse_network_name(network: str):
        parts = network.split('-')
        return {
            "network_name": '-'.join(parts[0:-2]),
            "team_id": int(parts[-2]),
            "challenge_id": int(parts[-1]),
        }

    @staticmethod
    def run_container(client: Client, team: Team, blueprint_obj: ContainerBlueprint):
        ulimit = docker.types.Ulimit(name="nofile", soft=10000, hard=20000)
        mem_limit = blueprint_obj.mem_limit or "128m"
        cpus = 0.1
        if blueprint_obj.cpus:
            if float(blueprint_obj.cpus) > 0.5:
                raise BusinessLogicError("Please set cpus to a value under 0.5")

            cpus = float(blueprint_obj.cpus)


        parsed_ram = DOCKER_MEM_REGEX.match(mem_limit)
        ram_number = int(parsed_ram.group(1))
        ram_postfix = parsed_ram.group(2)

        swap_mem = f"{round(ram_number * 1.5)}{ram_postfix}"
        mem_resv = f"{round(ram_number * 0.8)}{ram_postfix}"

        # I am not setting a kernel memory limit
        # As you it is deprecated
        # See https://github.com/torvalds/linux/commit/0158115f702b0ba208ab0b5adf44cae99b3ebcc7
        ctr = client.containers.run(
            blueprint_obj.image,
            environment=blueprint_obj.render_environment(team.seed),
            name=ContainerInstance.render_container_name(team.id, blueprint_obj.name, blueprint_obj.challenge_id),
            detach=True,
            # Default period of o .1 second
            cpu_period=100000,
            cpu_quota=round(cpus * DOCKER_QUOTA_CONST),
            pids_limit=512,
            mem_limit=mem_limit,
            mem_reservation=mem_resv,
            memswap_limit=swap_mem,
            ulimits=[ulimit],
        )

        # Get bridge network and remove to isolate challenge containers
        # From reaching out
        net = client.networks.list(names=[f"^{DOCKER_BRIDGE}$"])
        if net[0]:
            net[0].disconnect(ctr)

        return ctr

    @staticmethod
    def connect_networks(client: Client, team: Team, blueprint_obj: ContainerBlueprint, ctr):
        if blueprint_obj.networks:
            for network in blueprint_obj.networks:
                netconf = None
                is_static_net = not isinstance(blueprint_obj.networks, list)

                if isinstance(blueprint_obj.netconfs, dict):
                    netconf = blueprint_obj.netconfs.get(network)

                networkname = ContainerInstance.render_network_name(team.id, network, blueprint_obj.challenge_id)
                net_exists = client.get_network_by_name(networkname)
                if not net_exists:
                    ipam = None
                    if netconf and netconf.ipam:
                        ipam_pools = [
                            docker.types.IPAMPool(subnet=pool.subnet) for pool in netconf.ipam.config
                        ]
                        ipam = docker.types.IPAMConfig(pool_configs=ipam_pools)

                    net = client.networks.create(name=networkname, driver="overlay", internal=True, attachable=True, ipam=ipam)

                    ipaddr = None
                    if is_static_net and blueprint_obj.networks[network]:
                        ipaddr = blueprint_obj.networks[network].ipv4_address or None

                    net.connect(ctr, aliases=[blueprint_obj.hostname], ipv4_address=ipaddr)

                else:
                    ## Network was created for another container apart of the challenge
                    try:
                        ipaddr = None
                        if is_static_net and blueprint_obj.networks[network]:
                            ipaddr = blueprint_obj.networks[network].ipv4_address
                        net_exists.connect(ctr, aliases=[blueprint_obj.hostname], ipv4_address=ipaddr)
                    except docker.errors.APIError as err:
                        # Check if container is already connected to the network
                        if not NET_ERR_REGEX.search(str(err)):
                            raise err

    @classmethod
    def get_service_instances(cls):
        from ...challenge.models.Challenge import Challenge
        from ...team.models.Team import Team
        from ...event.models.Event import Event

        qr = (db.session.query(
                cls.id,
                cls.blueprint,
                cls.team_id,
                Challenge.name.label("challenge_name"),
                Team.name.label("team_name"),
                Challenge.id.label("challenge_id"),
                func.count(cls.id.distinct()).label("containers"),
                Challenge.event_id.label("event_id"),
                Event.name.label("event_name")
            )
            .outerjoin(Team, cls.team_id == Team.id)
            .outerjoin(Event, Team.event_id == Event.id)
            .outerjoin(ContainerBlueprint, cls.blueprint == ContainerBlueprint.id)
            .outerjoin(Challenge, ContainerBlueprint.challenge_id == Challenge.id)
            .group_by(Challenge.id, cls.team_id)
            .all())

        return qr

    @classmethod
    def get_service_group(cls, challenge_id: int, team_id: int) -> list[SerializedContainerInstance]:
        blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()

        blueprint_ids = [blueprint.id for blueprint in blueprints]

        instances = db.session.scalars(
            select(cls)
            .where(cls.blueprint.in_(blueprint_ids), cls.team_id == team_id)
        ).all()


        return [instance.serialize() for instance in instances]

    @classmethod
    def get_instance_group(cls, challenge_id: int, team_id: int):
        from ...challenge.models.ContainerBlueprint import ContainerBlueprint

        blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()

        blueprint_ids = [blueprint.id for blueprint in blueprints]

        instances = db.session.scalars(
            select(cls)
            .where(cls.blueprint.in_(blueprint_ids), cls.team_id == team_id)
        ).all()
        return instances

    @classmethod
    def get_instance_by_id(cls, instance_id: int):
        return cls.query.filter_by(id=instance_id).first()

    @classmethod
    def remove_instance_group(cls, challenge_id: int, team_id: int) -> list[str]:
        from ...challenge.models.ContainerBlueprint import ContainerBlueprint

        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, cls.render_lock_key(team_id, challenge_id))

        if lock.acquire(blocking=False):
            instances = cls.get_instance_group(challenge_id, team_id)

            DOCKER_HOST = get_app_config("DOCKER_HOST")
            client = get_client(DOCKER_HOST)
            for instance in instances:
                instance.remove()

            blueprints = ContainerBlueprint.get_for_challenge(challenge_id)
            indv_ctrs = []
            for blueprint in blueprints:
                for net in blueprint.networks:
                    net_obj = client.get_network_by_name(cls.render_network_name(team_id, net, challenge_id))
                    if net_obj:
                        try:
                            # In the case of a team game there might be vnc containers
                            # That are not the requesting user's
                            connected_ctrs = client.api.inspect_network(net_obj.id)['Containers']
                            for connected_ctr in connected_ctrs:
                                # Internal swarm overlay container
                                # We cannot disconnect ths
                                if not connected_ctr == f"lb-{net_obj.name}":
                                    indv_ctrs.append(connected_ctr)
                                    net_obj.disconnect(connected_ctr)
                            net_obj.remove()
                        except Exception:
                            pass
            lock.release()
            return indv_ctrs
        else:
            raise BusinessLogicError("Challenge is already being started/reset")

    @classmethod
    def start_instance_group(cls, challenge_id: int, team_id: int) -> list[str]:
        from ...challenge.models.ContainerBlueprint import ContainerBlueprint
        from ...team.models.Team import Team

        redis_client = get_redis_client(3)
        lock = redis_lock.Lock(redis_client, cls.render_lock_key(team_id, challenge_id))

        if lock.acquire(blocking=False):
            blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()
            team = Team.query.filter_by(id=team_id).first()

            ctrs = []
            networks = []
            try:
                for blueprint in blueprints:
                    ## Networks should get appened first to ensure they get properly
                    ## cleaned up
                    if blueprint.networks:
                        networks.extend(blueprint.networks)
                    ctrs.append(cls.create_container_instance(blueprint.id, team, commit=False))

            except Exception as err:
                DOCKER_HOST = get_app_config("DOCKER_HOST")
                client = get_client(DOCKER_HOST)
                for ctr in ctrs:
                    ctr.remove()
                for net in set(networks):
                    net_obj = client.get_network_by_name(cls.render_network_name(team_id, net, challenge_id))
                    if net_obj:
                        ## There is a potential race condition where the daemon has deleted the network
                        ## But the network is not fully removed from NETDB
                        try:
                            net_obj.remove()
                        except Exception:
                            pass
                db.session.rollback()
                lock.release()

                logger.error(str(err))
                raise BusinessLogicError("Challenge failed to start, please contact support") from err
            db.session.commit()
            lock.release()
            return networks
        else:
            raise BusinessLogicError("Challenge is already being started/reset")

    @classmethod
    def stop_instance_group(cls, challenge_id: int, team_id: int):
        instances = cls.get_instance_group(challenge_id, team_id)
        for instance in instances:
            instance.stop()

    @classmethod
    def delete_instance_group(cls, challenge_id: int, team_id: int):
        instances = cls.get_instance_group(challenge_id, team_id)
        try:
            cls.remove_instance_group(challenge_id, team_id)

            for instance in instances:
                instance.delete(commit=False, remove_docker_ctr=False)

        except Exception:
            db.session.rollback()
        db.session.commit()

    @classmethod
    def get_instance_group_networks(cls, challenge_id: int, team_id: int) -> list[str]:
        from ...challenge.models.ContainerBlueprint import ContainerBlueprint

        blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()

        networks = []
        for blueprint in blueprints:
            if blueprint.networks:
                networks.extend(blueprint.networks)
        net_names = []
        for net in set(networks):
            net_names.append(cls.render_network_name(team_id, net, challenge_id))

        return net_names


    def logs(self, tail: int = 200) -> str:
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)
        try:
            ctr = client.containers.get(self.dockerid)
            return ctr.logs(tail=tail).decode('utf-8')
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found, please recycle") from exc

    def raw_logs(self) -> str:
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)
        try:
            ctr = client.containers.get(self.dockerid)
            return io.BytesIO(ctr.logs())
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found, please recycle") from exc

    def status(self) -> SerializedInstanceStats:
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)
        ctr = client.containers.get(self.dockerid)

        image = "unknown"
        if ctr.image.attrs["RepoTags"]:
            # if the image is tagged, show the tag
            image = ctr.image.attrs["RepoTags"][0]
        elif ctr.image.attrs["RepoDigests"]:
            # if this image is no longer tagged, show the digest instead
            image = ctr.image.attrs["RepoDigests"][0]

        data = {
            "id": self.id,
            "name": ctr.name,
            "image": image,
            "docker_id": self.dockerid,
            "status": ctr.status,
            "env": ctr.attrs['Config']['Env'],
        }

        return SerializedInstanceStats(**data)

    def serialize(self) -> SerializedContainerInstance:
        return SerializedContainerInstance(
            id=self.id,
            blueprint=self.blueprint,
            team_id=self.team_id,
            hostip=self.hostip,
            dockerid=self.dockerid,
       )


    def restart(self):
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)
        try:
            ctr = client.containers.get(self.dockerid)
            ctr.restart()
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found please recycle") from exc

    def recycle(self):
        blueprint_obj = ContainerBlueprint.query.filter_by(id=self.blueprint).first()
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)

        try:
            ctr = client.containers.get(self.dockerid)

            if ctr.status == DOCKER_RUNNING:
                ctr.kill()

            ctr.remove()

        except docker.errors.NotFound:
            pass

        finally:
            new_ctr = self.run_container(client, self.team, blueprint_obj)

            self.connect_networks(client, self.team, blueprint_obj, new_ctr)

            self.dockerid = new_ctr.id
            db.session.commit()

    def remove(self):
        client = get_client(self.hostip)

        try:
            ctr = client.containers.get(self.dockerid)
            ctr.remove(force=True)
        except docker.errors.NotFound:
            pass

    def stop(self):
        client = get_client(self.hostip)
        try:
            ctr = client.containers.get(self.dockerid)
            ctr.stop(timeout=5)
        except docker.errors.NotFound:
            pass

    def delete(self, remove_docker_ctr=True, commit=True):
        if remove_docker_ctr:
            self.remove()

        db.session.delete(self)

        if commit:
            db.session.commit()


