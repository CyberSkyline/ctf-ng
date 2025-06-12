import logging
import yaml
import cattrs
from typing import Dict, Any, TextIO, Union
from pathlib import Path
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from cattrs.strategies import configure_union_passthrough
from typing import get_origin, get_args, Union

from .compose import ComposeFile
from .service import Template
from .challenge_info import ChallengeInfo, TextHint, ImageHint
from .rewriter import rewrite_aliases

logger = logging.getLogger(__name__)

def is_dict_list_union(tp):
    # Check if the type is a Union containing both dict and list types (any parameterization)
    if get_origin(tp) is Union:
        args = set(get_origin(arg) or arg for arg in get_args(tp))
        return dict in args and list in args
    return False

def dict_list_union_hook_gen(converter: cattrs.Converter):

    def dict_list_union_hook(val, tp):
        # Get the union arguments
        args = get_args(tp)
        # Try to structure as dict or list, depending on input
        if isinstance(val, dict):
            dict_type = next(arg for arg in args if (get_origin(arg) or arg) is dict)
            return converter.structure(val, dict_type)
        elif isinstance(val, list):
            list_type = next(arg for arg in args if (get_origin(arg) or arg) is list)
            return converter.structure(val, list_type)
        else:
            raise ValueError("Expected dict or list")
    
    return dict_list_union_hook

class ComposeYamlParser:
    """Parser for Docker Compose YAML files with challenge extensions and template rewriting."""
    
    def __init__(self):
        self.converter = self._setup_converter()
    
    def _setup_converter(self) -> cattrs.Converter:
        """Set up cattrs converter with proper union handling and custom hooks."""
        converter = cattrs.Converter()
        
        # Configure union passthrough for compose union types
        configure_union_passthrough(TextHint | ImageHint | int | bool | str | Template | None, converter)
        
        # Register hooks for handling x-challenge extension
        cf_st_hook = make_dict_structure_fn(ComposeFile, converter, challenge=cattrs.override(rename="x-challenge"))
        cf_unst_hook = make_dict_unstructure_fn(ComposeFile, converter, challenge=cattrs.override(rename="x-challenge"))
        converter.register_structure_hook(ComposeFile, cf_st_hook)
        converter.register_unstructure_hook(ComposeFile, cf_unst_hook)
        # converter.register_structure_hook(ComposeFile, self._structure_compose_file)

        converter.register_structure_hook_func(is_dict_list_union, dict_list_union_hook_gen(converter))
        
        return converter
    
    def _structure_compose_file(self, data: Dict[str, Any], _: type) -> ComposeFile:
        """Structure hook for ComposeFile that handles x-challenge extension."""
        # Extract x-challenge if present
        challenge_data = data.pop('x-challenge', None)
        challenge = None
        
        if challenge_data:
            logger.debug("Found x-challenge data, structuring ChallengeInfo")
            challenge = self.converter.structure(challenge_data, ChallengeInfo)
        
        # Structure the rest of the compose file
        compose_data = {**data, 'challenge': challenge} if challenge else data
        
        # Use default structuring for the cleaned data
        return self.converter.structure(compose_data, ComposeFile)
    
    def parse_file(self, file_path: Union[str, Path]) -> ComposeFile:
        """Parse a Docker Compose YAML file from disk."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Compose file not found: {file_path}")
        
        logger.info(f"Parsing compose file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.parse_stream(f)
    
    def parse_stream(self, stream: TextIO) -> ComposeFile:
        """Parse a Docker Compose YAML from a stream."""
        return self.parse_string(stream.read())
    
    def parse_string(self, yaml_content: str) -> ComposeFile:
        """Parse a Docker Compose YAML from a string."""
        logger.debug("Starting YAML parsing with template rewriting")
        
        # Step 1: Create a YAML loader and add template constructor
        loader = yaml.BaseLoader(yaml_content)
        
        try:
            # Step 2: Rewrite aliases/templates
            logger.debug("Rewriting aliases and templates")
            events = list(rewrite_aliases(loader))
            
            # Step 3: Reconstruct YAML from events
            logger.debug("Reconstructing YAML from rewritten events")
            rewritten_yaml = yaml.emit(events)
            logger.debug(f"Rewritten YAML:\n{rewritten_yaml}")
            
            # Step 4: Parse the rewritten YAML into a dictionary
            parsed_data = yaml.load(rewritten_yaml, Loader=yaml.Loader)
            
            # Step 5: Structure into ComposeFile using cattrs
            logger.debug("Structuring data into ComposeFile")
            compose_file = self.converter.structure(parsed_data, ComposeFile)
            
            logger.info("Successfully parsed compose file")
            return compose_file
            
        except Exception as e:
            logger.error(f"Error parsing compose file: {e}")
            raise
        finally:
            loader.dispose()
    
    def to_yaml(self, compose_file: ComposeFile) -> str:
        """Convert a ComposeFile back to YAML string."""
        # Unstructure the compose file to a dictionary
        data = self.converter.unstructure(compose_file)
        
        # Handle x-challenge extension
        if 'challenge' in data and data['challenge']:
            data['x-challenge'] = data.pop('challenge')
        
        # Convert to YAML
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

# Convenience functions for easy usage
def parse_compose_file(file_path: Union[str, Path]) -> ComposeFile:
    """Parse a Docker Compose file."""
    parser = ComposeYamlParser()
    return parser.parse_file(file_path)

def parse_compose_string(yaml_content: str) -> ComposeFile:
    """Parse Docker Compose YAML from a string."""
    parser = ComposeYamlParser()
    return parser.parse_string(yaml_content)
