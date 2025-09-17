from ..models.ContainerInstance import ContainerInstance
from flask import Response

def admin_exec(instance_id: int) -> Response:
    container = ContainerInstance.find_by_id(instance_id)
    print(container.hostip)
    print(container.dockerid)

    headers = {
       "Cache-Control": "max-age=60",
       "Host-Ip": container.hostip,
       "docker-id" : container.dockerid,
    }

    return Response("", status=200, headers=headers)
