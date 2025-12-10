from ..models.ContainerInstance import ContainerInstance
from flask import Response
from CTFd.utils import get_app_config

def admin_exec(instance_id: int) -> Response:
    container = ContainerInstance.find_by_id(instance_id)
    psk = get_app_config("EXEC_PSK")

    headers = {
       "Cache-Control": "max-age=60",
       "Host-Ip": container.hostip,
       "docker-id" : container.dockerid,
       "psk" : psk,
    }

    return Response("", status=200, headers=headers)
