from flask_restx import Namespace, Resource
from ..controllers.start_containers import start_containers

from ...core.utils.api_responses import (
    error_response,
    success_response,
)

container_namespace = Namespace('containers', description='containers')


@container_namespace.route('/<int:challenge_id>/start')
@container_namespace.param("challenge_id", "Challenge ID")
class ImportChallenge(Resource):
    @container_namespace.doc(
        description='Start a challenges containers',
        params={'challenge_id': 'Challenge id to start containers for'},
        responses={
            200: 'Sucess',
            400: 'Bad request',
        },
    )
    def get(self, **kwargs):
        res = start_containers(kwargs['challenge_id'], 1)
        return success_response({ 'started': res })
