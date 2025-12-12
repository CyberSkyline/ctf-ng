from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer
from ..constants import CHALLENGER_NET_NAME
from ...core import BusinessLogicError

def recycle_containers(challenge_id: int, team_id: int, current_user: int) -> bool:
    indv_ctr = IndvidualContainer.get_user_indvidual_container(current_user.id)
    indv_ctr.disconnect_from_networks()

    indv_ctrs = ContainerInstance.recycle_instance_group(challenge_id, team_id)

    networks = ContainerInstance.start_instance_group(challenge_id, team_id)

    if CHALLENGER_NET_NAME not in set(networks):
        raise BusinessLogicError("Challenge has no challenger network")


    indv_ctr.connect_to_network(ContainerInstance.render_network_name(team_id, CHALLENGER_NET_NAME, challenge_id))

    for ctr in indv_ctrs:
        indv_ctr_obj = IndvidualContainer.get_indvidual_container_by_dockerid(ctr)
        if indv_ctr_obj:
            indv_ctr_obj.disconnect_from_networks()
            indv_ctr_obj.connect_to_network(ContainerInstance.render_network_name(team_id, CHALLENGER_NET_NAME, challenge_id))

    return True
