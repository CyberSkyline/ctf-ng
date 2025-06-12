from typing import Literal, Any
from attrs import define, field

from parser.rewriter import Template

@define
class Service:
    # Required fields
    image: str
    hostname: str

    # Ignored fields
    build: Any = None
    ports: Any = None
    stdin_open: Any = None
    tty: Any = None
    
    # Potentially ignored fields
    logging: Any = None
    healthcheck: Any = None
    develop: Any = None

    # Optional fields
    command: str | list[str] | None = None
    entrypoint: str | list[str] | None = None
    environment: dict[str, Template | str] | list[str] | None = None
    networks: list[str] | dict[str, None] | None = None
    cap_add: list[Literal['NET_ADMIN', 'SYS_PTRACE']] | None = None
    mem_limit: int | str | None = None
    memswap_limit: int | str | None = None
    cpus: float | str | None = None

    # Unknown if it should be included
    user: str | None = None
    
    # Extension fields
    # NOTE: Extension fields (x-*) need to be handled separately during parsing
    # as attrs doesn't support pattern-based aliases like "x-*"
    extensions: dict[str, Any] | None = field(default=None)
