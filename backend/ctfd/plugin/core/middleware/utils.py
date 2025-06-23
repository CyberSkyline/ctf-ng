"""
Utility functions for parameter validation and model filtering.
/backend/ctfd/plugin/core/middleware/utils.py
"""

from flask import abort
from typing import Any
from dataclasses import dataclass
from sqlalchemy import and_, inspect
from ..utils.logger import get_logger
from ..utils.api_responses import error_response
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.types import Boolean, DateTime
from sqlalchemy.orm.attributes import InstrumentedAttribute
from dateutil.parser import parse as parse_date

logger = get_logger(__name__)


@dataclass
class MiddlewareResult:
    success: bool
    data: Any = None
    error_response: tuple = None


def params_check_valid(params, model):
    """Check if the request has valid parameters for the given model."""
    relationships = inspect(model).relationships
    related_models = [rel.mapper.class_ for rel in relationships]
    prefix = model.__name__.lower() + "_"
    params = [param[len(prefix) :] if param.startswith(prefix) else param for param in params]

    for param in params:
        if not hasattr(model, param):
            if not hasattr(model, "__mapper__") or not any(
                hasattr(rm, param.replace(rm.__name__.lower() + "_", "")) for rm in related_models
            ):
                logger.error(f"Invalid parameter '{param}' for model {model.__name__}.")
                return False

    # removed too strict single parameter uniqueness check
    return True


def get_param_values(params, request) -> MiddlewareResult:
    """Extract values for the given parameters from the request."""
    values = []
    for param in params:
        # -----Vital: Check path params, and query string params-----#
        value = request.view_args.get(param) or request.args.get(param)
        if value is None:
            logger.error(f"Missing required parameter '{param}' in request.")
            error_resp = error_response(
                f"Missing required parameter '{param}' in request.",
                "missing_parameter",
                400,
            )
            return MiddlewareResult(success=False, error_response=error_resp)
        values.append(value)

    return MiddlewareResult(success=True, data=values)


def filter_model_by_fields(model, filters):
    """Filter the given model by the provided field values."""
    mapper = inspect(model)
    conditions = []

    for key, value in filters.items():
        # Directly check if the key is a column in the model
        prefix = model.__name__.lower() + "_"
        key = key[len(prefix) :] if key.startswith(prefix) else key
        if key in mapper.columns:
            condition_add(conditions, model, key, value)
            continue
        # If not, check if it's a relationship attribute
        matched = False
        for rel in mapper.relationships:
            related_model = rel.mapper.class_
            related_mapper = inspect(related_model)
            prefix = related_model.__name__.lower() + "_"

            if key in related_mapper.columns:
                # If found, use the original `key`
                condition_add_rel(conditions, model, related_model, key, rel.key, value)
                matched = True
                break

            # If the original key wasn't found, check the stripped version
            stripped_key = key.replace(prefix, "")
            if stripped_key in related_mapper.columns:
                # If found, use the `stripped_key`
                condition_add_rel(conditions, model, related_model, stripped_key, rel.key, value)
                matched = True
                break

        if not matched:
            logger.error(f"Invalid filter key '{key}' for model {model.__name__}.")
            error_resp = error_response(
                f"Invalid filter key '{key}' for model {model.__name__}.",
                "invalid_parameter",
                400,
            )
            return MiddlewareResult(success=False, error_response=error_resp)

    try:
        result = model.query.filter(and_(*conditions)).one()
        return MiddlewareResult(success=True, data=result)
    except NoResultFound:
        logger.error(f"No {model.__name__} found with filters {filters}.")
        error_resp = error_response(
            f"No {model.__name__} found with filters {filters}.",
            "not_found",
            404,
        )
        return MiddlewareResult(success=False, error_response=error_resp)
    except MultipleResultsFound:
        logger.error(f"Multiple {model.__name__}s found with filters {filters}.")
        error_resp = error_response(
            f"Multiple {model.__name__}s found with filters {filters}.",
            "not_found",
            409,
        )
        return MiddlewareResult(success=False, error_response=error_resp)


def condition_add(conditions, model, key, value):
    """Add a condition to the filter based on the model's column type."""
    if isinstance(getattr(model, key).type, Boolean):
        bool_value = value.lower() in ["true", "1", "yes"]
        conditions.append(getattr(model, key).is_(bool_value))
    elif isinstance(getattr(model, key).type, DateTime):
        try:
            value = parse_date(value)
        except ValueError:
            logger.error(f"Invalid date format for value '{value}'.")
            abort(400, description="Invalid date format for value'.")
        conditions.append(getattr(model, key) == value)
    else:
        conditions.append(getattr(model, key) == value)

    return conditions


def condition_add_rel(conditions, model, rel_model, key, rel_key, value):
    """Add a condition for a relationship attribute."""
    related_col = getattr(rel_model, key)
    rel_attr: InstrumentedAttribute = getattr(model, rel_key)
    if isinstance(getattr(rel_model, key).type, Boolean):
        bool_value = value.lower() in ["true", "1", "yes"]
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
