from ..utils.get_client import get_client
from ..utils.get_docker_hosts import get_docker_hosts
from typing import TypedDict

class SeralizedDockerInfo(TypedDict):
    containers_running: int
    os: str
    cpus: int
    memory: int
    ip: str

def get_stats():

    DOCKER_HOST = get_docker_hosts()
    client_info = []
    for host in DOCKER_HOST:
        client = get_client(host)
        client_info.append(client.api.info())

    return [  SeralizedDockerInfo(
        containers_running = host["ContainersRunning"],
        os = host["OperatingSystem"],
        cpus = host["NCPU"],
        memory = host["MemTotal"],
        ip = host["Swarm"]["NodeAddr"],
    ) for host in client_info]
