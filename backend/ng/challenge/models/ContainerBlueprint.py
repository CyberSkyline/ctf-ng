from typing import Any, Literal
from collections.abc import Callable

from CTFd.models import db
from sqlalchemy.orm import Mapped

from ...core.utils.validator import BaseValidator

MAX_CONTAINER_BLUEPRINT_NAME_LENGTH = 128
MAX_CONTAINER_BLUEPRINT_IMAGE_LENGTH = 1024
MAX_CONTAINER_BLUEPRINT_HOSTNAME_LENGTH = 256

MAX_CONTAINER_BLUEPRINT_MEM_LIMIT_LENGTH = 256
MAX_CONTAINER_BLUEPRINT_MEMSWAP_LIMIT_LENGTH = 256
MAX_CONTAINER_BLUEPRINT_USER_LENGTH = 256


class ContainerBlueprint(db.Model):
    __tablename__ = "ng_container_blueprints"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(), nullable=True)
    image: Mapped[str] = db.Column(db.String(MAX_CONTAINER_BLUEPRINT_IMAGE_LENGTH), nullable=False)
    hostname: Mapped[str] = db.Column(db.String(MAX_CONTAINER_BLUEPRINT_HOSTNAME_LENGTH), nullable=False)
    stdin_open: Mapped[bool] = db.Column(db.Boolean, nullable=True)
    tty: Mapped[bool] = db.Column(db.Boolean, nullable=True)
    command: Mapped[list[str]] = db.Column(db.PickleType, nullable=True)
    entrypoint: Mapped[str | list[str] | None] = db.Column(db.PickleType, nullable=True)
    environment: Mapped[dict[str, str | Callable[[str], str]] | list[str] | None] = db.Column(db.PickleType, nullable=True)
    networks: Mapped[list[str] | dict[str, None] | None] = db.Column(db.PickleType, nullable=True)
    cap_add: Mapped[list[Literal['NET_ADMIN', 'SYS_PTRACE']] | None] = db.Column(db.PickleType, nullable=True)
    mem_limit: Mapped[int | str | None] = db.Column(db.String(MAX_CONTAINER_BLUEPRINT_MEM_LIMIT_LENGTH), nullable=True)
    memswap_limit: Mapped[int | str | None] = db.Column(db.String(MAX_CONTAINER_BLUEPRINT_MEMSWAP_LIMIT_LENGTH), nullable=True)
    cpus: Mapped[float | None] = db.Column(db.Numeric, nullable=True)
    user: Mapped[str | None] = db.Column(db.String(MAX_CONTAINER_BLUEPRINT_USER_LENGTH), nullable=True)
    challenge_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("ng_challenges.id"), nullable=False, index=True)

    def __repr__(self):
        return f"<NgContainerBlueprint {self.id}>"

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the container blueprint data.
        :param data: The container blueprint data to validate.
        :return: The validated data.
        """
        validator = BaseValidator()

        validator.validate_string(
            data,
            "image",
            MAX_CONTAINER_BLUEPRINT_IMAGE_LENGTH,
            required=True,
            friendly_name="Container Image",
        )
        validator.validate_string(
            data,
            "hostname",
            MAX_CONTAINER_BLUEPRINT_HOSTNAME_LENGTH,
            required=True,
            friendly_name="Container Hostname",
        )
        validator.validate_model_id(
            data,
            "challenge_id",
            "Challenge",
            required=True,
            friendly_name="Challenge ID",
        )
        validator.validate_boolean(
            data,
            "stdin_open",
            required=False,
            friendly_name="Stdin Open",
        )
        validator.validate_boolean(
            data,
            "tty",
            required=False,
            friendly_name="TTY",
        )

        # TODO - Validate all of the remaining optional fields

        return validator.validate()

    @classmethod
    def create_container_blueprint(
        cls,
        image: str,
        hostname: str,
        challenge_id: int,
        stdin_open: bool | None = None,
        tty: bool | None = None,
        command: list[str] | None = None,
        entrypoint: str | list[str] | None = None,
        environment: dict[str, str | Callable[[str], str]] | list[str] | None = None,
        networks: list[str] | dict[str, None] | None = None,
        cap_add: list[Literal['NET_ADMIN', 'SYS_PTRACE']] | None = None,
        mem_limit: int | str | None = None,
        memswap_limit: int | str | None = None,
        cpus: float | None = None,
        user: str | None = None,
        commit=True,
    ):
        try:
            ## Removed the validator as it currently does not support lists
            validated_data = {
                    "image": image,
                    "hostname": hostname,
                    "challenge_id": challenge_id,
                    "stdin_open": stdin_open,
                    "tty": tty,
                    "command": command,
                    "entrypoint": entrypoint,
                    "environment": environment,
                    "networks": networks,
                    "cap_add": cap_add,
                    "mem_limit": mem_limit,
                    "memswap_limit": memswap_limit,
                    "cpus": cpus,
                    "user": user,
            }
            blueprint = cls(**validated_data)
            db.session.add(blueprint)
            db.session.flush()
            if commit:
                db.session.commit()
            return blueprint
        except Exception as e:
            db.session.rollback()
            raise e

    def render_environment(self, team_seed: str) -> dict[str, str] | list[str]:
        if not self.environment:
            return {}

        if isinstance(self.environment, list):
            return self.environment

        return {k: (v(team_seed) if isinstance(v, Callable) else v) for k, v in self.environment.items()}