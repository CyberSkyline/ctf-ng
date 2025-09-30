import docker
from ..constants import DOCKER_RUNNING
from CTFd.utils import get_app_config


class Client(docker.DockerClient):
    def get_running(self, ctr):
        ctr = self.containers.get(ctr)
        if ctr.status != DOCKER_RUNNING:
            ctr.start()
        return ctr

    def get_network_by_name(self, name):
        return self.networks.list(names=[f"^{name}$"])[0]

    def pull_image(self, image):
        auth = {
            "username": get_app_config("CONTAINER_REGISTRY_USER"),
            "password": get_app_config("CONTAINER_REGISTRY_PASSWORD"),
        }
        self.images.pull(image, auth_config=auth)
