from ...team.models.Team import Team
from ...user.models.User import User
from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ...challenge.models.ContainerBlueprint import ContainerBlueprint

def start_containers(challenge_id: int, team_id: int, current_user: User) -> bool:
    blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()
    team = Team.query.filter_by(id=team_id).first()

    ctrs = []
    networks = []
    for blueprint in blueprints:
        ctrs.append(ContainerInstance.create_container_instance(blueprint.id, team))
        if blueprint.networks:
            networks.append(*blueprint.networks)

    indvidual_ctr = IndvidualContainer.create_indvidual_container(current_user.id)
    indvidual_ctr.disconnect_from_networks()

    for network in set(networks):
        indvidual_ctr.connect_to_network(ContainerInstance.render_network_name(team_id, network, challenge_id))

    return True
