from typing import Iterator

class Warnings:

    def __init__(self, key: str, self_warnings: Iterator[str] | None, field_warnings: Iterator['Warnings'] | None) -> None:
        self.key = key
        self.self_warnings = self_warnings
        self.field_warnings = field_warnings
    
    def render(self, indent: int = 0) -> str:
        indent_str = ' ' * indent
        result = f"{indent_str}{self.key}:\n"
        if self.self_warnings:
            for warning in self.self_warnings:
                result += f"{indent_str}  - {warning}\n"
        if self.field_warnings:
            for field_warning in self.field_warnings:
                result += field_warning.render(indent + 2)
        return result