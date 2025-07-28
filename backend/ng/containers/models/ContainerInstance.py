from CTFd.models import db
import docker
from ..utils.get_client import get_client
from ... import config
from .. constants import DOCKER_RUNNING
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ...core.utils.validator import BaseValidator

class ContainerInstance(db.Model):
    __tablename__ = "ng_container_instances"
    id = db.Column(db.Integer, primary_key=True)
    blueprint = db.Column(db.Integer, db.ForeignKey("ng_container_blueprints.id"), nullable=False)
    team = db.Column(db.Integer, db.ForeignKey("ng_teams.id"), nullable=False)
    hostip = db.Column(db.String(255), nullable=False)
    dockerid = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ContainerInstance {self.id}>"

    @classmethod
    def create_container_instance(cls, blueprint: int, team: int, commit: bool = True):
        blueprint_obj = ContainerBlueprint.query.filter_by(id=blueprint).first()

        exists = cls.query.filter_by(blueprint=blueprint, team=team).first()
        if exists:
            return exists

        client = get_client(config.DOCKER_HOST)

        ctr = None
        try:
            ctr = client.containers.get(
                cls.render_container_name(team, blueprint_obj.hostname, blueprint_obj.challenge_id)
            )
            if ctr.status != DOCKER_RUNNING:
                ctr.start()

        ## Container Needs created
        except docker.errors.NotFound:
            networks = []
            if blueprint_obj.networks:
                for network in blueprint_obj.networks:
                    networkname = cls.render_network_name(team, network, blueprint_obj.challenge_id)
                    net_exists = client.networks.list(names=[networkname])
                    if len(net_exists) == 0:
                        networks.append(client.networks.create(name=networkname, internal=True, attachable=True))
                    else:
                        ## Network was created for another container apart of the challenge
                        networks.append(net_exists[0])

            ## Need To detach or it will hang
            ## (TODO) add in env vars and what not
            ctr = client.containers.run(
                blueprint_obj.image,
                name=cls.render_container_name(team, blueprint_obj.hostname, blueprint_obj.challenge_id),
                detach=True
            )

            for network in networks:
                network.connect(ctr, aliases=[blueprint_obj.hostname])

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
