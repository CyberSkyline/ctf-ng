from ...user.models.User import User
from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ..constants import CHALLENGER_NET_NAME
from ...core import BusinessLogicError

def start_containers(challenge_id: int, team_id: int, current_user: User) -> bool:
    networks = ContainerInstance.start_instance_group(challenge_id, team_id)

    indvidual_ctr = IndvidualContainer.create_indvidual_container(current_user.id)
    indvidual_ctr.disconnect_from_networks()

    if CHALLENGER_NET_NAME not in set(networks):
        raise BusinessLogicError("Challenge has no challenger network")

    indvidual_ctr.connect_to_network(ContainerInstance.render_network_name(team_id, CHALLENGER_NET_NAME, challenge_id))
    return True
