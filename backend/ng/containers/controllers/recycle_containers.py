from CTFd.utils import get_app_config
from .start_containers import start_containers
from ..utils.get_client import get_client
from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ...challenge.models.ContainerBlueprint import ContainerBlueprint

def recycle_containers(challenge_id: int, team_id: int, current_user: int) -> bool:
    indv_ctr = IndvidualContainer.get_user_indvidual_container(current_user.id)
    indv_ctr.disconnect_from_networks()

    instances = ContainerInstance.get_instance_group(challenge_id, team_id)

    DOCKER_HOST = get_app_config("DOCKER_HOST")
    client = get_client(DOCKER_HOST)
    for instance in instances:
        instance.remove()

    blueprints = ContainerBlueprint.get_for_challenge(challenge_id)
    for blueprint in blueprints:
        for net in blueprint.networks:
            net_obj = client.get_network_by_name(ContainerInstance.render_network_name(team_id, net, challenge_id))
            if net_obj:
                try:
                    net_obj.remove()
                except Exception:
                    pass

    return start_containers(challenge_id, team_id, current_user)
