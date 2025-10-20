"""
Custom SQLAlchemy types for handling edge cases gracefully
"""

import typing as t
import sqlalchemy


class EnumWithUnknown(sqlalchemy.Enum):
    """
    SQLAlchemy Enum type that gracefully handles unknown/removed enum values
    by mapping them to a designated UNKNOWN enum member.
    """
    def __init__(self, *enums, **kw: t.Any):
        super().__init__(*enums, **kw)

        if "_adapted_from" in kw:
            self._unknown_value = kw["_adapted_from"]._unknown_value
        else:
            self._unknown_value = kw.get("unknown_value", None)
            if self._unknown_value is None:
                raise ValueError(
                    "unknown_value must be specified for EnumWithUnknown"
                )

    def adapt(self, impltype, **kw):
        """
        Override adapt to ensure _unknown_value is copied to adapted instances
        """
        kw["_adapted_from"] = self
        return super().adapt(impltype, **kw)

    def _object_value_for_elem(self, elem):
        """
        Override to handle unknown values gracefully by returning the unknown_value
        instead of raising LookupError
        """
        try:
            return self._object_lookup[elem]
        except (KeyError, LookupError):
            return self._unknown_value
