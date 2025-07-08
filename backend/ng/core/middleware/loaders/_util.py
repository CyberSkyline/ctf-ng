from functools import wraps
from flask import g
from ...exceptions import ValidationError, NotFoundError
from ...utils import get_models
import enum

class LoaderType(str, enum.Enum):
    PARAM = "param"
    BODY = "body"

def _generate_loader_decorator(source: LoaderType, model_name: str, input_key: str, output_key: str):
    def _body():
        # Check for JSON data
        if not hasattr(g, "json_data"):
            raise ValueError("JSON data not found in request context")

        # Check if the key is in the JSON
        if input_key not in g.json_data:
            raise ValidationError(f"Missing required key in JSON data: {input_key}")
        
        return g.json_data[input_key]

    def _param(kwargs):
        if input_key not in kwargs:
            raise ValidationError(f"Missing required parameter: {input_key}")
        
        return kwargs[input_key]

    """Generate a loader decorator for a given model."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the output_key is already in kwargs, error if it is
            if output_key in kwargs:
                raise ValueError(f"Argument '{output_key}' already exists in kwargs")

            # Select the corresponding model class based on the model_name
            models = get_models()
            model_class = models.get(model_name)
            if not model_class:
                raise ValueError(f"Model '{model_name}' not found")
        
            # Get the model ID based on the source type
            if source == LoaderType.BODY:
                model_id = _body()
            elif source == LoaderType.PARAM:
                model_id = _param(kwargs)
            else:
                raise ValueError(f"Invalid loader type: {source}")
            
            # Look up the object in the database
            instance = model_class.find_by_id(model_id)
            if not instance:
                raise NotFoundError(f"{model_name} with ID {model_id} not found")
            
            # Set value on kwargs
            kwargs[output_key] = instance
            return f(*args, **kwargs)

        return decorated_function

    return decorator