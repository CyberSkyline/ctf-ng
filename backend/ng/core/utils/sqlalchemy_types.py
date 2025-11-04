"""
Custom SQLAlchemy types for handling edge cases gracefully
"""

import typing as t
import sqlalchemy


class EnumWithUnknown(sqlalchemy.Enum):
    """
    SQLAlchemy Enum type that gracefully handles unknown/removed enum values
    by mapping them to a designated UNKNOWN enum member.

    Based on: https://grimoire.ca/mysql/sqlalchemy-mysql-enums
    """
    def __init__(self, *enums, **kw: t.Any):
        # Call parent first - SQLAlchemy's Enum accepts **kw and ignores unknown keys
        super().__init__(*enums, **kw)

        # SQLAlchemy sets the _adapted_from keyword argument sometimes, which contains
        # a reference to the original type - but won't include original keyword arguments,
        # so we need to handle that here.
        self._unknown_value = kw["_adapted_from"]._unknown_value if "_adapted_from" in kw else kw.get("unknown_value", None)
        if self._unknown_value is None:
            raise ValueError("unknown_value should be a member of the enum")

    def adapt(self, cls, **kw):
        """
        Override adapt to ensure _unknown_value is passed to adapted instances.
        We pass it via unknown_value in kwargs so the new instance can pick it up.
        """
        kw.setdefault("unknown_value", self._unknown_value)
        return super().adapt(cls, **kw)

    def _object_value_for_elem(self, elem):
        """
        Override to handle unknown values gracefully by returning the unknown_value
        instead of raising LookupError
        """
        try:
            return self._object_lookup[elem]
        except (KeyError, LookupError):
            return self._unknown_value
