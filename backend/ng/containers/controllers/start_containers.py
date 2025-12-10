from CTFd.models import db
from CTFd.utils import get_app_config
from ...team.models.Team import Team
from ...user.models.User import User
from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ..utils.get_client import get_client
from ...challenge.models.ContainerBlueprint import ContainerBlueprint
from ..constants import CHALLENGER_NET_NAME
from ...core import BusinessLogicError

def start_containers(challenge_id: int, team_id: int, current_user: User) -> bool:
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
            ctrs.append(ContainerInstance.create_container_instance(blueprint.id, team, commit=False))

    except Exception as err:
        DOCKER_HOST = get_app_config("DOCKER_HOST")
        client = get_client(DOCKER_HOST)
        for ctr in ctrs:
            ctr.remove()
        for net in set(networks):
            net_obj = client.get_network_by_name(ContainerInstance.render_network_name(team_id, net, challenge_id))
            if net_obj:
                net_obj.remove()

        db.session.rollback()
        raise BusinessLogicError(f"Challenge failed to start, please contact support: {str(err)}") from err

    db.session.commit()

    indvidual_ctr = IndvidualContainer.create_indvidual_container(current_user.id)
    indvidual_ctr.disconnect_from_networks()


    if CHALLENGER_NET_NAME not in set(networks):
        raise BusinessLogicError("Challenge has no challenger network")

    indvidual_ctr.connect_to_network(ContainerInstance.render_network_name(team_id, CHALLENGER_NET_NAME, challenge_id))
    return True
