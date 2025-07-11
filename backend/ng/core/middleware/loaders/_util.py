from functools import wraps
from flask import g, request
from ...exceptions import ValidationError, NotFoundError
from ...utils import get_models
import enum
import inspect

class LoaderType(str, enum.Enum):
    PARAM = "param"
    BODY = "body"

def check_output_exists(kwargs: dict, output_key: str):
    """Check if the output_key already exists in kwargs."""
    if output_key in kwargs:
        raise ValueError(f"Argument '{output_key}' already exists in kwargs")
    return True

def get_model_class(model_name: str):
    """Select the corresponding model class based on the model_name"""
    models = get_models()
    model_class = models.get(model_name)
    if not model_class:
        raise ValueError(f"Model '{model_name}' not found")
    return model_class

def get_json_val(input_key: str):
    """Get the value from JSON data in the request context."""
    if not hasattr(g, "json_data"):
        raise ValueError("JSON data not found in request context")
    
    if input_key not in g.json_data:
        raise ValidationError(f"Missing required key in JSON data: {input_key}")
    
    return g.json_data[input_key]

def get_param_val(kwargs: dict, input_key: str):
    """Get the value from kwargs based on the input_key."""
    if input_key in kwargs:
        return kwargs[input_key]
    if input_key in request.args or request.view_args:
        return request.args.get(input_key) or request.view_args.get(input_key)
    raise ValidationError(f"Missing required key in request parameters: {input_key}")

def generate_loader_decorator(source: LoaderType, model_name: str, input_key: str, output_key: str):
    """Generate a loader decorator for a given model."""
    def decorator(f):
        sig = inspect.signature(f)

        @wraps(f)
        def decorated_function(*args, **kwargs):
            check_output_exists(kwargs, output_key)
            model_class = get_model_class(model_name)
        
            # Get the model ID based on the source type
            if source == LoaderType.BODY:
                model_id = get_json_val(input_key)
            elif source == LoaderType.PARAM:
                model_id = get_param_val(kwargs, input_key)
            else:
                raise ValueError(f"Invalid loader type: {source}")
            
            # Look up the object in the database
            instance = model_class.find_by_id(model_id)
            if not instance:
                raise NotFoundError(f"{model_name} with ID {model_id} not found")
            kwargs[output_key] = instance
            return f(*args, **kwargs)

        return decorated_function

    return decorator