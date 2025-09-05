from CTFd.models import db
import docker
from sqlalchemy import func, select
from typing import TypedDict

from ..utils.get_client import get_client
from ..utils.Client import Client
from ... import config
from .. constants import DOCKER_RUNNING, DOCKER_BRIDGE
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ...team.models.Team import Team

class SerializedInstanceStats(TypedDict):
    id: int
    name: str
    image: str
    docker_id: str
    status: str

class SerializedContainerInstance(TypedDict):
    id: int
    blueprint: int
    team: int
    hostip: str
    dockerid: str

class ContainerInstance(db.Model):
    __tablename__ = "ng_container_instances"
    id = db.Column(db.Integer, primary_key=True)
    blueprint = db.Column(db.Integer, db.ForeignKey("ng_container_blueprints.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid: str = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ContainerInstance {self.id}>"

    @classmethod
    def find_by_id(cls, instance_id: int):
        return cls.query.filter_by(id=instance_id).first()

    @classmethod
    def create_container_instance(cls, blueprint: int, team: Team, commit: bool = True):
        blueprint_obj = ContainerBlueprint.query.filter_by(id=blueprint).first()

        db_exists = cls.query.filter_by(blueprint=blueprint, team=team.id).first()

        client = get_client(config.DOCKER_HOST)

        if db_exists:
            try:
                ctr = client.get_running(db_exists.dockerid)
            except docker.errors.NotFound:
                ctr = cls.run_container(client, team, blueprint_obj)
                cls.connect_networks(client, team, blueprint_obj, ctr)

                db_exists.dockerid = ctr.id
                db.session.commit()

            return db_exists

        ctr = None
        try:
            ctr = client.get_running(
                cls.render_container_name(team, blueprint_obj.hostname, blueprint_obj.challenge_id)
            )

        ## Container Needs created
        except docker.errors.NotFound:
            ## Need To detach or it will hang
            ## (TODO) add in env vars and what not
            ctr = cls.run_container(client, team, blueprint_obj)

        cls.connect_networks(client, team, blueprint_obj, ctr)

        container_instance = cls(
            blueprint=blueprint,
            team=team,
            hostip=config.DOCKER_HOST,
            dockerid=ctr.id,
        )

        db.session.add(container_instance)
        if commit:
            db.session.commit()
        return container_instance

    @staticmethod
    def render_container_name(team_id: int, hostname: str, challenge_id: int) -> str:
        return f"{team_id}-{hostname}-{challenge_id}"

    @staticmethod
    def render_network_name(team_id: int, network_name: str, challenge_id: int) -> str:
        return f"{network_name}-{team_id}-{challenge_id}"

    @staticmethod
    def parse_network_name(network: str):
        parts = network.split('-')
        return {
            "network_name": parts[0],
            "team_id": int(parts[1]),
            "challenge_id": int(parts[2]),
        }

    @staticmethod
    def run_container(client: Client, team: Team, blueprint_obj: ContainerBlueprint):
        ctr = client.containers.run(
            blueprint_obj.image,
            environment=blueprint_obj.render_environment(team.seed),
            name=ContainerInstance.render_container_name(team.id, blueprint_obj.hostname, blueprint_obj.challenge_id),
            detach=True,
        )

        # Get bridge network and remove to isolate challenge containers
        # From reaching out
        net = client.networks.list(names=[DOCKER_BRIDGE])
        net[0].disconnect(ctr)

        return ctr

    @staticmethod
    def connect_networks(client, team, blueprint_obj, ctr):
        if blueprint_obj.networks:
            for network in blueprint_obj.networks:
                networkname = ContainerInstance.render_network_name(team, network, blueprint_obj.challenge_id)
                net_exists = client.networks.list(names=[networkname])
                if len(net_exists) == 0:
                    net = client.networks.create(name=networkname, internal=True, attachable=True)
                    net.connect(ctr, aliases=[blueprint_obj.hostname])

                else:
                    ## Network was created for another container apart of the challenge
                    net_exists[0].connect(ctr, aliases=[blueprint_obj.hostname])


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
    def get_instance_by_id(cls, instance_id: int):
        return cls.query.filter_by(id=instance_id).first()

    def logs(self, tail: int = 200) -> str:
        client = get_client(config.DOCKER_HOST)
        try:
            ctr = client.containers.get(self.dockerid)
            return ctr.logs(tail=tail).decode('utf-8')
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found, please recycle") from exc

    def status(self) -> SerializedInstanceStats:
        client = get_client(config.DOCKER_HOST)
        ctr = client.containers.get(self.dockerid)

        data = {
            "id": self.id,
            "name": ctr.name,
            "image": ctr.image.tags[0] if ctr.image.tags else "unknown",
            "docker_id": self.dockerid,
            "status": ctr.status,
        }

        return SerializedInstanceStats(**data)

    def serialize(self) -> SerializedContainerInstance:
        return SerializedContainerInstance(
            id=self.id,
            blueprint=self.blueprint,
            team=self.team_id,
            hostip=self.hostip,
            dockerid=self.dockerid,
       )


    def restart(self):
        client = get_client(config.DOCKER_HOST)
        try:
            ctr = client.containers.get(self.dockerid)
            ctr.restart()
        except docker.errors.NotFound as exc:
            raise ValueError("Container not found please recycle") from exc

    def recycle(self):
        blueprint_obj = ContainerBlueprint.query.filter_by(id=self.blueprint).first()
        client = get_client(config.DOCKER_HOST)

        try:
            ctr = client.containers.get(self.dockerid)

            if ctr.status == DOCKER_RUNNING:
                ctr.kill()

            ctr.remove()

        except docker.errors.NotFound:
            pass

        finally:
            new_ctr = self.run_container(client, self.team_id, blueprint_obj)

            self.connect_networks(client, self.team_id, blueprint_obj, new_ctr)

            self.dockerid = new_ctr.id
            db.session.commit()
