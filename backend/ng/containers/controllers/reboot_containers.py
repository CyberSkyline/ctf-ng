from ..models.ContainerInstance import ContainerInstance

def reboot_containers(challenge_id: int, team_id: int, current_user: int) -> bool:
    instances = ContainerInstance.get_instance_group(challenge_id, team_id)

    for instance in instances:
        instance.restart()

    return True
