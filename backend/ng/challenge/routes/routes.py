from flask import request
import base64
from flask_restx import Namespace, Resource

from ..controllers.import_yaml import import_yaml
from ...core.middleware import (
    admin_endpoint,
)

from ...core.utils import (
    error_response,
    success_response,
)

challenge_namespace = Namespace('challenges', description='challenge managment')


@challenge_namespace.route('/import')
class ImportChallenge(Resource):
    @admin_endpoint()
    @challenge_namespace.doc(
        description='Import a ng yaml definition',
        responses={
            200: 'Sucess',
            400: 'Bad request - Returns Yaml Parser Error',
        },
    )

    @admin_endpoint(json_required=True)
    def post(self):
        data = request.get_json()
        payload = base64.urlsafe_b64decode(data['yaml'])
        res = import_yaml(payload.decode('utf-8'))

        if res['success']:
            return success_response(res)
        else:
            return error_response(res['error'], 'yaml_parser', 400)
