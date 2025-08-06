from ..models.ContainerInstance import ContainerInstance

def recycle_container(instance_id):
    instance = ContainerInstance.get_instance_by_id(instance_id)
    instance.recycle()
