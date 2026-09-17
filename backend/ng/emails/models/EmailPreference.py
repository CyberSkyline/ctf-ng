"""
Defines the EmailPreference model for per-user email notification opt-outs.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from CTFd.models import db

from ...core.utils.sqlalchemy_types import EnumWithUnknown
from ...core.utils.validator import BaseValidator


class EmailCategory(str, Enum):
    UNKNOWN = "unknown"
    SUPPORT_EMAILS = "support_emails"
    TEAM_EMAILS = "team_emails"


class EmailPreference(db.Model):
    __tablename__ = "ng_email_preferences"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable = False,
        index = True
    )
    category = db.Column(
        EnumWithUnknown(
            EmailCategory,
            values_callable = lambda t: [str(item.value) for item in t],
            unknown_value = EmailCategory.UNKNOWN,
            native_enum = False
        ),
        nullable = False
    )
    enabled = db.Column(db.Boolean, default = True, nullable = False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "category"),
    )

    def __repr__(self):
        return f"<EmailPreference user={self.user_id} category={self.category.value} enabled={self.enabled}>"

    @classmethod
    def is_enabled(cls, user_id: int, category: EmailCategory) -> bool:
        """
        Check if a user has a given email category enabled.
        A missing row means the category is enabled (opt-out model).
        """
        row = cls.query.filter_by(user_id = user_id, category = category).first()
        return row.enabled if row else True

    @classmethod
    def set_preference(
        cls,
        user_id: int,
        category: EmailCategory,
        enabled: bool,
        commit: bool = True
    ) -> EmailPreference:
        """
        Set a user's preference for an email category, creating or updating
        the row as needed.
        """
        row = cls.query.filter_by(user_id = user_id, category = category).first()
        if row:
            row.enabled = enabled
        else:
            row = cls(user_id = user_id, category = category, enabled = enabled)
            db.session.add(row)

        if commit:
            db.session.commit()

        return row

    @classmethod
    def get_all_for_user(cls, user_id: int) -> dict[str, bool]:
        """
        Get the effective preference for every known email category,
        defaulting to enabled for categories with no stored row.
        """
        rows = {
            row.category: row.enabled
            for row in cls.query.filter_by(user_id = user_id).all()
        }
        return {
            category.value: rows.get(category, True)
            for category in EmailCategory
            if category != EmailCategory.UNKNOWN
        }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate an email preference update payload.
        """
        validator = BaseValidator()

        for category in EmailCategory:
            if category != EmailCategory.UNKNOWN:
                validator.validate_boolean(data, category.value, required=False)

        return validator.validate()

    @classmethod
    def update_preferences(cls, user_id: int, data: dict[str, Any]) -> dict[str, bool]:
        """
        Validate and apply email preference updates for a user.
        """
        validated_data = cls.validate(data)

        for category in EmailCategory:
            if category.value in validated_data:
                cls.set_preference(user_id, category, validated_data[category.value], commit = False)
        db.session.commit()

        return cls.get_all_for_user(user_id)
