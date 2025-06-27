from flask import request
import base64
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only

from ..controllers.import_yaml import import_yaml
from ...core.middleware import (
        authed_user_required,
)

from ...core.utils.api_responses import (
    error_response,
    success_response,
)

challenge_namespace = Namespace('challenges', description='challenge managment')


@challenge_namespace.route('/import')
class ImportChallenge(Resource):
    @authed_only
    @authed_user_required
    @challenge_namespace.doc(
        description='Import a ng yaml definition',
        responses={
            200: 'Sucess',
            400: 'Bad request - Returns Yaml Parser Error',
        },
    )
    def post(self):
        data = request.get_json()
        payload = base64.urlsafe_b64decode(data['yaml'])
        res = import_yaml(payload.decode('utf-8'))
        print(res)

        if res['success']:
            return success_response(res)
        else:
            return error_response(res['error'], 'yaml_parser', 400)
