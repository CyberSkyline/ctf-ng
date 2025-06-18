"""
Functions to convert SQLAlchemy query results into Python dicts.
/backend/ctfd/plugin/core/utils/data_conversion.py
"""

from typing import Any
from sqlalchemy.engine import Row
from plugin.core.utils.logger import get_logger

logger = get_logger(__name__)


def rows_to_dicts(rows: list[Row], field_mapping: dict[str, str] = None) -> list[dict[str, Any]]:
    """Convert SQLAlchemy Row objects to dictionaries with optional field mapping.

    Args:
        rows (list[Row]): SQLAlchemy query result rows
        field_mapping (dict[str, str], optional): Maps row attribute names to dict keys.
            Format: {"row_attr": "dict_key"}. If None, uses row attribute names as keys.

    Returns:
        list[dict[str, Any]]: List of dictionaries with converted data

    """
    if not rows:
        return []

    result = []

    for row in rows:
        row_dict = {}

        for key in row._fields:
            try:
                # Attempt to get the attribute from the row object.
                value = getattr(row, key)
            except AttributeError:
                logger.critical(
                    "Query-to-Object Mismatch: A field expected from the query was not found on the row object.",
                    extra={
                        "context": {
                            "missing_key": key,
                            "available_keys": list(row._fields),
                            "row_object_type": str(type(row)),
                        }
                    },
                )
                # None to prevent a server crash - but logs the error
                value = None

            dict_key = field_mapping.get(key, key) if field_mapping else key
            row_dict[dict_key] = value

        result.append(row_dict)

    return result


def row_to_dict(row: Row, field_mapping: dict[str, str] = None) -> dict[str, Any]:
    """Convert a single SQLAlchemy Row object to a dictionary.

    Args:
        row (Row): SQLAlchemy query result row
        field_mapping (dict[str, str], optional): Maps row attribute names to dict keys

    Returns:
        dict[str, Any]: Dictionary with converted data
    """
    if not row:
        return {}

    return rows_to_dicts([row], field_mapping)[0]
