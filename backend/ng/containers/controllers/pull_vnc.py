from ..utils.get_client import get_client
from CTFd.utils import get_app_config

def pull_vnc(pulling_user: int) -> bool:
    docker_hosts = get_app_config("DOCKER_HOST").split(",")
    vnc_image = get_app_config("NOVNC_CONTAINER")


    for docker_host in docker_hosts:
        client = get_client(docker_host)
        client.pull_image(vnc_image, pulling_user, "VNC")

    return True
