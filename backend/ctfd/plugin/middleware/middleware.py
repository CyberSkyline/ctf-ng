from functools import wraps
from flask import request, abort,g
from sqlalchemy import and_, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import Boolean, DateTime
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from CTFd.utils.user import get_current_user
from CTFd.models import db
from datetime import datetime
from dateutil.parser import parse as parse_date
from plugin.user.models.User import User
from plugin.event.models.Event import Event
from plugin.team.models.Team import Team
from plugin.utils.api_responses import error_response
from plugin.utils.logger import get_logger


logger = get_logger(__name__)

"""
For all lookup decorators, generic/common parameters are expected to be prefixed with 'user_', 'event_', 'team_' or other model in future.
For example, 'user_id', 'event_name', 'team_id'.
This allows the decorator to handle both specific and generic parameter names.
"""

def lookup(model, params: list[str], attach_as: str = None):
    """
    Generic decorator to retrieve a model instance by given parameters.
    Capable of handling both specific and generic parameters.
    As well as parameters present through relationships.
    ie: @lookup(Team, ['event_id', 'user_id']) works because Team has related TeamMembers who have user_ids

    Args:
        model: Model class to query.
        params (list[str]): List of parameter names to check in the request.
        attach_as (str): Name to attach the found instance to kwargs (defaults to model.__name__.lower()).

    The retrieved instance is attached to the `kwargs` as `attach_as`.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if params_check_valid(params, model) is False:
                return error_response(
                    f"Invalid parameters {params} for model {model.__name__}.",
                    "invalid_parameter",
                    400,
            )
            values = get_param_values(params, request)
            if isinstance(values, tuple):
                return values
            results = filter_model_by_fields(model, dict(zip(params, values)))
            if isinstance(results, tuple):
                return results
            attach_name = attach_as or model.__name__.lower()
            kwargs[attach_name] = results
            return f(*args, **kwargs)
        return wrapped
    return decorator

def authed_user_required(f):
    """Decorator that ensures user is authenticated and attaches user to g.user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return error_response("User not found in session", "auth", 401)
        g.user = current_user
        return f(*args, **kwargs)
    return decorated_function
                              


def json_body_required(f):
    """Decorator that ensures request has JSON body and attaches it to g.json_data"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return error_response("Request must have a JSON body", "body", 400)
        data = request.get_json()
        if not data:
            return error_response("JSON is malformed or invalid", "body", 400)
        g.json_data = data
        return f(*args, **kwargs)

    return decorated_function


def handle_integrity_error(f):
    """Decorator that wraps controller calls and handles IntegrityError consistently"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            # Rollback the session to avoid leaving it in a broken state
            db.session.rollback()
            logger.error(
                "Database integrity error in route handler",
                extra={
                    "context": {
                        "function": f.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "error": str(e),
                    }
                },
            )
            return error_response(
                "Database constraint error. Please check your request and try again.",
                "database",
                409,
            )

    return decorated_function


"""Utility functions for parameter validation and model filtering"""



def params_check_valid(params, model):
    """Check if the request has valid parameters for the given model."""
    values = []
    relationships = inspect(model).relationships
    related_models = [rel.mapper.class_ for rel in relationships]
    prefix = model.__name__.lower() + "_"
    params = [param[len(prefix):] if param.startswith(prefix) else param for param in params]


    for param in params:
        if not hasattr(model, param):
            if not hasattr(model, '__mapper__') or not any (hasattr(rm, param.replace(rm.__name__.lower()+'_',"")) for rm in related_models):
                logger.error(f"Invalid parameter '{param}' for model {model.__name__}.")
                return False
                

    if len(params) == 1:
        column = getattr(model, params[0])
        if not column.unique and not column.primary_key:
            logger.error(f"Single Parameter '{params[0]}' is not unique or primary key in model {model.__name__}.")
            return False
    return True
    

def get_param_values(params, request):
    """Extract values for the given parameters from the request."""
    values = []
    for param in params:
        value = request.args.get(param)
        if value is None:
            logger.error(f"Missing required parameter '{param}' in request.")
            return error_response(
                f"Missing required parameter '{param}' in request.",
                "missing_parameter",
                400,
            )
        values.append(value)
    return values

def filter_model_by_fields(model, filters):
    """Filter the given model by the provided field values."""
    mapper = inspect(model)
    conditions = []
    
    for key, value in filters.items():
        # Directly check if the key is a column in the model
        prefix = model.__name__.lower() + "_"
        key = key[len(prefix):] if key.startswith(prefix) else key        
        if key in mapper.columns:
            condition_add(conditions, model, key, value)
            continue
        # If not, check if it's a relationship attribute
        matched = False
        for rel in mapper.relationships:
            related_model = rel.mapper.class_
            related_mapper = inspect(related_model)
            prefix = related_model.__name__.lower() + "_"

            if (key := key) in related_mapper.columns or (key := key.replace(prefix,"")) in related_mapper.columns:
                condition_add_rel(conditions,model,related_model,key,rel.key,value)
                matched = True
                break

        if not matched:
            logger.error(f"Invalid filter key '{key}' for model {model.__name__}.")
            return error_response(
                f"Invalid filter key '{key}' for model {model.__name__}.",
                "invalid_parameter",
                400,
            )
    try:
        result = model.query.filter(and_(*conditions)).one()
    except NoResultFound:
        logger.error(f"No {model.__name__} found with filters {filters}.")
        return error_response(
            f"No {model.__name__} found with filters {filters}.",
            "not_found",
            404,
        )
    except MultipleResultsFound:
        logger.error(f"Multiple {model.__name__}s found with filters {filters}.")
        return error_response(
            f"Multiple {model.__name__}s found with filters {filters}.",
            "not_found",
            409,
        )
    return result


def condition_add(conditions, model, key, value):
    """Add a condition to the filter based on the model's column type."""
    if isinstance(getattr(model, key).type, Boolean):
        bool_value = value.lower() in ['true', '1', 'yes']
        conditions.append(getattr(model, key).is_(bool_value))
    elif isinstance(getattr(model, key).type, DateTime):
        try:
            value = parse_date(value)
        except ValueError:
            logger.error(f"Invalid date format for value '{value}'.")
            abort(400, description=f"Invalid date format for value'.")
        conditions.append(getattr(model, key) == value)
    else:
        conditions.append(getattr(model, key) == value)

    return conditions

def condition_add_rel(conditions,model,rel_model,key,rel_key,value):
    """Add a condition for a relationship attribute."""
    related_col = getattr(rel_model, key)
    rel_attr: InstrumentedAttribute = getattr(model, rel_key)
    if isinstance(getattr(rel_model, key).type, Boolean):
        bool_value = value.lower() in ['true', '1', 'yes']
        conditions.append(rel_attr.any(related_col.is_(bool_value)))
    elif isinstance(getattr(rel_model, key).type, DateTime):
        try:
            value = parse_date(value)
        except ValueError:
            logger.error(f"Invalid date format for value '{value}'")
            abort(400, description=f"Invalid date format for value '{value}'")
        conditions.append(rel_attr.any(related_col == value))
    else:
        conditions.append(rel_attr.any(related_col == value))
    return conditions
        
        
            