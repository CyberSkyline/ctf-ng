from ..utils.get_client import get_client
from CTFd.utils import get_app_config
from typing import TypedDict
from ... import config

class SeralizedDockerInfo(TypedDict):
    containers_running: int
    os: str
    cpus: int
    memory: int

def get_stats():

    DOCKER_HOST = get_app_config("DOCKER_HOST")
    client = get_client(DOCKER_HOST)
    client_info = client.api.info()

    return SeralizedDockerInfo(
        containers_running = client_info["ContainersRunning"],
        os = client_info["OperatingSystem"],
        cpus = client_info["NCPU"],
        memory = client_info["MemTotal"],
    )
