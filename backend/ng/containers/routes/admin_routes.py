from flask_restx import Namespace, Resource
from flask import request
from ...challenge.utils import generate_seed
from ...challenge.models import Challenge
from ..controllers.get_stats import get_stats
from ..controllers.admin_exec import admin_exec
from ..controllers.pull_vnc import pull_vnc
from ..models.ContainerInstance import ContainerInstance

from ...core.middleware import (
    admin_endpoint,
)

from ...core.middleware.loaders import (
    LoaderType,
    load_team,
    load_container_instance,
    load_challenge
)

from ...core.utils import (
    success_response,
)

admin_container_namespace = Namespace("admin containers", description="admin containers")

@admin_container_namespace.route("")
class Containers(Resource):
    @admin_container_namespace.doc(
        description="Get service groups by teams",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, **kwargs):
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
    def get(self, **kwargs):
        res = get_stats()
        return success_response(res)

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/services")
class ServiceGroup(Resource):
    @admin_container_namespace.doc(
        description="Get Container instance for a challenge given a team",
        params={
            "challenge_id": "Id of the challenge",
            "team_id": "Id of the team",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, challenge_id, team_id, **kwargs):
        res = ContainerInstance.get_service_group(challenge_id, team_id)
        return success_response(res)

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/variables")
class ContainerVars(Resource):
    @admin_container_namespace.doc(
        description="Get Container instance variables for a challenge given a team",
        params={
            "challenge_id": "Id of the challenge",
            "team_id": "Id of the team",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @load_team(LoaderType.PARAM)
    @load_challenge(LoaderType.PARAM)
    @admin_endpoint()
    def get(self, challenge: Challenge, team, **kwargs):
      # create answer variable to question map to ensure seeding is consistent with questions/env
      qids = {q.answer_variable_id: q.id  for q in challenge.questions}

      values = {v.name: v.as_attr().template.eval(generate_seed(challenge.event_id, challenge.id, qids.get(v.id), team_seed=team.seed)) for v in challenge.variables}
      return success_response(values)

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
    def get(self, container_instance, container_instance_id, **kwargs):
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
    def post(self, container_instance, **kwargs):
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
    def post(self, container_instance, **kwargs):
        container_instance.recycle()
        return success_response(True)

@admin_container_namespace.route("/<int:container_instance_id>/logs")
class InstanceLogs(Resource):
    @admin_container_namespace.doc(
        description="Get Container Instance logs",
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
    def get(self, container_instance, **kwargs):
        res = container_instance.logs()
        return success_response(res)

@admin_container_namespace.route("/execforward")
class InstanceExec(Resource):
    @admin_container_namespace.doc(
        description="Forward exec service info to nginx. This should only be called by nginx. Pass container-id as a header",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def get(self, **kwargs):
        # Container id has to be a header because nginx was not rendering
        # the int variable in the url
        container_instance_id = int(request.headers.get('container-id'))
        return admin_exec(container_instance_id)

@admin_container_namespace.route("/vnc/pull")
class PullVnc(Resource):
    @admin_container_namespace.doc(
        description="Pull vnc container image onto docker host",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def post(self, current_user):
        pull_vnc(current_user.id)
        return success_response(True)
