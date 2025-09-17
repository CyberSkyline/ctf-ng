from typing import Iterable

class Warnings:
    def __init__(self, key: str, self_warnings: Iterable[str] | None, field_warnings: Iterable['Warnings'] | None) -> None:
        self.key = key
        self.self_warnings = list(self_warnings) if self_warnings else []
        self.field_warnings = list(field_warnings) if field_warnings else []

    def render(self, indent: int = 0) -> str:
        indent_str = ' ' * indent
        result = f"{indent_str}- {self.key}:\n"
        if self.self_warnings:
            for warning in self.self_warnings:
                result += f"{indent_str}  - {warning}\n"
        if self.field_warnings:
            for field_warning in self.field_warnings:
                result += field_warning.render(indent + 2)
        return result