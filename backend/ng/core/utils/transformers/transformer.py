from enum import Enum
from typing import Any, get_type_hints

from .base import HasTransform, Success, Failure, Result
from .meta import Field, FriendlyName, Untyped
from ...exceptions import ValidationError

from sqlalchemy.orm import Mapped

class FieldTransformStage(Enum):
    TYPE = 1
    MAIN = 2

class FieldTransformError:
    def __init__(self, stage: FieldTransformStage, errors: list[str]):
        self.stage = stage
        self.errors = errors

class FieldTransformer[T]:
    def __init__(self, field: str, typ: type[T] | None, friendly_name: str | None, transformers: list[HasTransform[T]]):
        self.field = field
        self.typ = typ.__origin__.__args__[0] if typ.__origin__ == Mapped[typ.__origin__.__args__[0]] else typ
        self.friendly_name = friendly_name or self.field.replace("_", " ").title()
        self.transformers = transformers

    def transform(self, value: Any) -> Result[T, FieldTransformError]:
        errors = []
        if self.typ is not None and value is not None and not isinstance(value, self.typ):
            errors.append(f"{self.friendly_name} must be of type {self.typ.__name__} not {type(value).__name__}")
            return FieldTransformError(FieldTransformStage.TYPE, errors)

        errors.clear()
        transformed_value: T = value
        for transformer in self.transformers:
            result = transformer.transform(transformed_value)
            if isinstance(result, Failure):
                errors.append(result.format_map({"field": self.friendly_name}))
            elif isinstance(result, Success):
                transformed_value = result.value

        if errors:
            return FieldTransformError(FieldTransformStage.MAIN, errors)

        return Success(transformed_value)

class MultiFieldTransformer[*T]:
    pass

class Transformer:
    def __init__(self, cls_: type):
        self.transformers: dict[str, FieldTransformer] = {}
        for (field, typ) in get_type_hints(cls_, include_extras=True).items():
            if hasattr(typ, '__metadata__'):
                self._add_field_transformer(field, typ, typ.__metadata__)

    def _add_field_transformer(self, field: str, typ: type, metadata: list[object]) -> None:
        field_name = field
        friendly_name = None
        transformers = []
        field_typ: type | None = typ
        for meta in metadata:
            if isinstance(meta, Field):
                field_name = meta.name
            elif isinstance(meta, FriendlyName):
                friendly_name = meta.friendly_name
            elif isinstance(meta, Untyped):
                field_typ = None
            elif isinstance(meta, HasTransform):
                transformers.append(meta)

        self.transformers[field_name] = FieldTransformer(
            field_name,
            field_typ,
            friendly_name,
            transformers
        )

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        errors = {}
        transformed_data: dict[str, Any] = {}
        for field, transformer in self.transformers.items():
            value = data.get(field)
            result = transformer.transform(value)
            if isinstance(result, FieldTransformError):
                errors[field] = result.errors
            elif isinstance(result, Success):
                transformed_data[field] = result.value

        if errors:
            raise ValidationError("Validation failed", errors)

        return transformed_data