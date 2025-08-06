from ..models.ContainerInstance import ContainerInstance

def restart_container(instance_id):
    instance = ContainerInstance.get_instance_by_id(instance_id)
    instance.restart()
