from flask_restx import Namespace, Resource
from ..controllers.get_stats import get_stats
from ..models.ContainerInstance import ContainerInstance

from ...core.middleware import (
    admin_endpoint,
)

from ...core.middleware.loaders import (
    LoaderType,
    load_container_instance,
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

@admin_container_namespace.route("/<int:container_instance_id>/status")
class InstanceStatus(Resource):
    @admin_container_namespace.doc(
        description="Get Container Instance status",
        params={
            "container_instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    @load_container_instance(source=LoaderType.PARAM)
    def get(self, container_instance, container_instance_id):
        res = container_instance.status()
        return success_response(res)


@admin_container_namespace.route("/<int:container_instance_id>/restart")
class InstanceRestart(Resource):
    @admin_container_namespace.doc(
        description="Restart a container",
        params={
            "container_instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    @load_container_instance(source=LoaderType.PARAM)
    def get(self, container_instance, container_instance_id):
        container_instance.restart()
        return success_response(True)

@admin_container_namespace.route("/<int:container_instance_id>/recycle")
class InstanceRecycle(Resource):
    @admin_container_namespace.doc(
        description="Deletes a container without deleting the backing db object",
        params={
            "container_instance_id": "Id of instance",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    @load_container_instance(source=LoaderType.PARAM)
    def get(self, container_instance):
        container_instance.recycle()
        return success_response(True)
