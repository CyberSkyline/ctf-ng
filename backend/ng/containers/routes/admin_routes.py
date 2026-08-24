from flask_restx import Namespace, Resource
from flask import request, send_file
from ...challenge.utils import generate_seed
from ...challenge.models import Challenge
from ..controllers.get_stats import get_stats
from ..controllers.admin_exec import admin_exec
from ..controllers.pull_vnc import pull_vnc
from ..controllers.recycle_containers import recycle_containers
from ..controllers.vnc import forward_vnc
from ..models.ContainerInstance import ContainerInstance
from ..models.IndvidualContainer import IndvidualContainer

from ...core.exceptions import NotFoundError
from ...core.middleware import (
    admin_endpoint,
    ag_grid_query,
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

@admin_container_namespace.route("/deployment")
class Deployments(Resource):
    @admin_container_namespace.doc(
        description="Get a page of deployments (ag-grid server-side row model)",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    @ag_grid_query
    def get(self, start_row, end_row, sort_model, filter_model, **kwargs):
        rows, total = ContainerInstance.find_deployments_paginated(sort_model, filter_model, start_row, end_row)
        return success_response({"rows": rows, "lastRow": total})


@admin_container_namespace.route("/deployment/<int:instance_id>")
class DeploymentDetail(Resource):
    @admin_container_namespace.doc(
        description="Get one deployment's summary by any instance id belonging to it",
        params={
            "instance_id": "Id of any container instance in the deployment",
        },
        responses={
            200: "Success",
            404: "Deployment not found"
        },
    )
    @admin_endpoint()
    def get(self, instance_id, **kwargs):
        deployment = ContainerInstance.find_deployment(instance_id)
        if deployment is None:
            raise NotFoundError(f"Deployment not found for instance {instance_id}")
        return success_response(deployment)


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

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/recycle")
class DeploymentRecycle(Resource):
    @admin_container_namespace.doc(
        description="Deletes a challenge deployment without deleting the backing db objects",
        params={
            "challenge_id": "Id of the challenge",
            "team_id": "Id of the team to recycle",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def post(self, challenge_id, team_id, **kwargs):
        res = recycle_containers(challenge_id, team_id)
        return success_response(res)

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/connect")
class DeploymentConnect(Resource):
    @admin_container_namespace.doc(
        description="Connect an admin's workspace to a deployment network",
        params={
            "challenge_id": "Id of the challenge",
            "team_id": "Id of the team to recycle",
        },
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def post(self, challenge_id, team_id, current_user, **kwargs):
        networks = ContainerInstance.get_instance_group_networks(challenge_id, team_id)

        indv_ctr = IndvidualContainer.get_user_indvidual_container(current_user.id)

        indv_ctr.disconnect_from_networks()

        for network in networks:
            indv_ctr.connect_to_network(network)

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

@admin_container_namespace.route("/<int:container_instance_id>/logs/download")
class DownloadInstanceLogs(Resource):
    @admin_container_namespace.doc(
        description="Download the instance logs",
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
        res = container_instance.raw_logs()
        return send_file(
            res,
            as_attachment=True,
            download_name=f"{container_instance.id}-logs.txt",
            mimetype="text/plain"
        )


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

@admin_container_namespace.route("/vnc/<int:user_id>/view")
class AdminViewVnc(Resource):
    @admin_container_namespace.doc(
        description="Forward no vnc info to nginx. This should only be called by nginx",
        params={"user_id": "User id for user's vnc instance"},
        responses={
            200: "Sucess",
            400: "Bad request"
        }
    )
    @admin_endpoint()
    def get(self, user_id, **kwargs):
        return forward_vnc(user_id)

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/stop")
class DeploymentStop(Resource):
    @admin_container_namespace.doc(
        description="Stop an instance group given the team and challenge",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def post(self, challenge_id: int, team_id: int, **kwargs):
        ContainerInstance.stop_instance_group(challenge_id, team_id)
        return success_response(True)

@admin_container_namespace.route("/challenge/<int:challenge_id>/team/<int:team_id>/delete")
class DeploymentDelete(Resource):
    @admin_container_namespace.doc(
        description="Delete an instance group given the team and challenge",
        responses={
            200: "Success",
            400: "Bad request"
        },
    )
    @admin_endpoint()
    def post(self, challenge_id: int, team_id: int, **kwargs):
        ContainerInstance.delete_instance_group(challenge_id, team_id)
        return success_response(True)
