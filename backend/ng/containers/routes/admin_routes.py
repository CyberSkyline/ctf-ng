from flask_restx import Namespace, Resource
from ..controllers.get_stats import get_stats
from ..controllers.restart_container import restart_container
from ..controllers.recycle_container import recycle_container
from ..models.ContainerInstance import ContainerInstance

from ...core.middleware import (
    admin_endpoint,
)

from ...core.utils import (
    success_response,
)

admin_container_namespace = Namespace("admin containers", description="admin containers")

@admin_container_namespace.route("/")
class Containers(Resource):
    @admin_container_namespace.doc(
        description="Get service groups by teams",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self):
        res = ContainerInstance.get_service_instances()
        return success_response(res)


@admin_container_namespace.route("/stats")
class NodeStats(Resource):
    @admin_container_namespace.doc(
        description="Get docker node stats",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self):
        res = get_stats()
        return success_response(res)

@admin_container_namespace.route("/<int:instance_id>/status")
class InstanceStatus(Resource):
    @admin_container_namespace.doc(
        description="Get Container Instance status",
        params={
            "instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, instance_id):
        res = ContainerInstance.get_instance_status(instance_id)
        return success_response(res)


@admin_container_namespace.route("/<int:instance_id>/restart")
class InstanceRestart(Resource):
    @admin_container_namespace.doc(
        description="Restart a container",
        params={
            "instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, instance_id):
        restart_container(instance_id)
        return success_response(True)

@admin_container_namespace.route("/<int:instance_id>/recycle")
class InstanceRecycle(Resource):
    @admin_container_namespace.doc(
        description="Deletes a container without deleting the backing db object",
        params={
            "instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, instance_id):
        recycle_container(instance_id)
        return success_response(True)
