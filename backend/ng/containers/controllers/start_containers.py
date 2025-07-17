from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ...challenge.models.ContainerBlueprint import ContainerBlueprint

def start_containers(challenge_id: int, team_id: int, current_user: int) -> bool:
    blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()

    ctrs = []
    networks = []
    for blueprint in blueprints:
        ctrs.append(ContainerInstance.create_container_instance(blueprint.id, team_id))
        networks.append(*blueprint.networks)

    indvidual_ctr = IndvidualContainer.create_indvidual_container(current_user)

    for network in set(networks):
        indvidual_ctr.connect_to_network(f'{network}-{team_id}-{challenge_id}')

    return True
