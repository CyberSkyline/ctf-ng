## Replace with john's package
import parser
from attrs import asdict
from ..models.ContainerBlueprint import ContainerBlueprint
from ..models.Hint import Hint
from ..models.Tag import Tag
from ..models.Question import Question
from ..models.Challenge import Challenge

def import_yaml(yaml):
    try:
        parsed_yaml = asdict(parser.parse_compose_string(yaml), filter=lambda y, x: x is not None)
    
        challenge_fields = {
            'name' : parsed_yaml['challenge']['name'],
            'description' : parsed_yaml['challenge']['description'],
            'icon' : parsed_yaml['challenge']['icon'],
        }
    
    
        challenge = Challenge.create_challenge(**challenge_fields)
    
        hints = list(map(lambda hint: Hint.create_hint(challenge_id=challenge.id, **hint), parsed_yaml['challenge']['hints']))
    
        questions = list(map(lambda question: Question.create_question(challenge_id=challenge.id, **question), parsed_yaml['challenge']['questions']))
    
        tags = list(map(lambda tag: Tag.create_tag(challenge_id=challenge.id, tag=tag), parsed_yaml['challenge']['tags']))
    
        containers = list(map(lambda kv: ContainerBlueprint.create_container_blueprint(challenge_id=challenge.id, **kv[1]), parsed_yaml['services'].items()))
        return {
            'success': True,
            'challenge': challenge,
        }
    except Exception as e:
        return {
            'success': False,
            'error' : str(e),
        }
