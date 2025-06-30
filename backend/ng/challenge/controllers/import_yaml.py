## Replace with john's package
from cyber_skyline.chall_parser.yaml_parser import parse_compose_string
from attrs import asdict
from ..models.ContainerBlueprint import ContainerBlueprint
from ..models.Hint import Hint
from ..models.Tag import Tag
from ..models.Question import Question
from ..models.Challenge import Challenge

def import_yaml(yaml):
    try:
        parsed_yaml = asdict(parse_compose_string(yaml), filter=lambda y, x: x is not None)

        challenge_fields = {
            'name' : parsed_yaml['challenge']['name'],
            'description' : parsed_yaml['challenge']['description'],
            'icon' : parsed_yaml['challenge']['icon'],
            'summary' : parsed_yaml['challenge'].get('summary', None)
        }

        challenge = Challenge.create_challenge(**challenge_fields)

        ## Need list conversion because of sql alchemey lazing loading relationships
        list(map(lambda hint: Hint.create_hint(challenge_id=challenge.id, **hint), parsed_yaml['challenge']['hints']))
        list(map(lambda question: Question.create_question(challenge_id=challenge.id, **question), parsed_yaml['challenge']['questions']))
        list(map(lambda tag: Tag.create_tag(challenge_id=challenge.id, tag=tag), parsed_yaml['challenge']['tags']))
        list(map(lambda kv: ContainerBlueprint.create_container_blueprint(challenge_id=challenge.id, **kv[1]), parsed_yaml['services'].items()))

        return {
            'success': True,
            'challenge': challenge,
        }
    except Exception as e:
        return {
            'success': False,
            'error' : str(e),
        }
