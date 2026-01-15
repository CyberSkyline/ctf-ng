from ..models.IndvidualContainer import IndvidualContainer
from flask import Response

def forward_vnc(user_id: int) -> Response:
    indv_ctr = IndvidualContainer.create_indvidual_container(user_id)

    host_port = indv_ctr.get_novnc_port()

    headers = {
       "Cache-Control": "no-store",
       "Host-Ip": indv_ctr.hostip,
       "Host-Port": host_port
    }

    return Response("", status=200, headers=headers)
