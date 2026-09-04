from ..utils.get_client import get_client
from ..utils.get_docker_hosts import get_docker_hosts
from CTFd.utils import get_app_config

def pull_vnc(pulling_user: int) -> bool:
    docker_hosts = get_docker_hosts()
    vnc_image = get_app_config("NOVNC_CONTAINER")


    client = get_client(docker_hosts[0])
    client.pull_image(vnc_image, pulling_user, "VNC")

    return True
