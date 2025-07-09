from ..models.ContainerInstance import ContainerInstance
from ...challenge.models.ContainerBlueprint import ContainerBlueprint

def start_containers(challenge_id, team_id):
    blueprints = ContainerBlueprint.query.filter_by(challenge_id=challenge_id).all()

    ctrs = []
    for blueprint in blueprints:
        ctrs.append(ContainerInstance.create_container_instance(blueprint.id, team_id))

    return True
