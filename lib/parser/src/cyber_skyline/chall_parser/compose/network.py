from typing import Iterator
from attrs import define, field
import attrs.validators as v
from cyber_skyline.chall_parser.compose.validators import is_ipv4_cidr

@define
class NetworkIPamConfig:
    subnet: str | None = field(default=None, validator=v.optional(is_ipv4_cidr))  # Subnet in CIDR format
    # No other fields are currently supported

@define
class NetworkIPam:
    driver: str | None = None  # IPAM driver, typically "default"
    config: list[NetworkIPamConfig] | None = None  # List of IPAM configurations

@define
class Network:
    """
    Represents a Docker Compose network configuration for CTF challenges.
    
    This is a heavily simplified network definition that only supports internal networks.
    External networks are ignored by production deployment for security reasons.
    """
    internal: bool | None = None # All networks must be internal (no external access)
    ipam: NetworkIPam | None = None # IP Address Management configuration

    def warnings(self) -> Iterator[str]:
        if self.internal is None:
            yield "internal field does not exist, this network will not be created in production"
        elif self.internal is False:
            yield "internal field is False, this network will not be created in production"