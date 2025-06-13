"""
/backend/ctfd/plugin/utils/data_conversion.py
Functions to convert SQLAlchemy query results into Python dicts.
"""

from typing import Any, List, Dict
from sqlalchemy.engine import Row


def rows_to_dicts(rows: List[Row], field_mapping: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Convert SQLAlchemy Row objects to dictionaries with optional field mapping.

    Args:
        rows (List[Row]): SQLAlchemy query result rows
        field_mapping (Dict[str, str], optional): Maps row attribute names to dict keys.
            Format: {"row_attr": "dict_key"}. If None, uses row attribute names as keys.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with converted data

    """
    if not rows:
        return []

    result = []

    for row in rows:
        row_dict = {}

        for key in row._fields:
            value = getattr(row, key)

            dict_key = field_mapping.get(key, key) if field_mapping else key
            row_dict[dict_key] = value

        result.append(row_dict)

    return result


def row_to_dict(row: Row, field_mapping: Dict[str, str] = None) -> Dict[str, Any]:
    """Convert a single SQLAlchemy Row object to a dictionary.

    Args:
        row (Row): SQLAlchemy query result row
        field_mapping (Dict[str, str], optional): Maps row attribute names to dict keys

    Returns:
        Dict[str, Any]: Dictionary with converted data
    """
    if not row:
        return {}

    return rows_to_dicts([row], field_mapping)[0]
