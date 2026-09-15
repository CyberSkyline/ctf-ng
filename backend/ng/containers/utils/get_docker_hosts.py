from CTFd.utils import get_app_config

def get_docker_hosts() -> list[str]:
    return get_app_config("DOCKER_HOST").split(",")
