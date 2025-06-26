"""
Event registration API routes.
"""

from flask import g
from flask_restx import Namespace, Resource

from ..controllers import (
    get_user_demographic,
    create_event_registration,
    join_event_controller,
)
from ...core.validation import (
    validate_event_registration_creation,
    validate_join_event,
)
from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
    admin_endpoint,
    load_event,
    load_event_from_request,
    require_event_is_joinable,
    check_demographic_eligibility,
    check_team_join_eligibility,
)
from ...core.docs import (
    GET_USER_DEMOGRAPHICS_DOC,
    JOIN_EVENT_DOC,
    CREATE_EVENT_REGISTRATION_DOC,
)

event_reg_namespace = Namespace("event_registration", description="Event Registration operations")


@event_reg_namespace.route("/<int:event_id>/demographics")
class UserDemographics(Resource):
    @user_endpoint()
    @event_reg_namespace.doc(**GET_USER_DEMOGRAPHICS_DOC)
    def get(self, event_id):
        """Get user demographics for an event"""
        result = get_user_demographic(g.user.id, event_id)
        return success_response(result)


@event_reg_namespace.route("/join/<int:event_id>")
class JoinEvent(Resource):
    @user_endpoint(json_required=True, validation_func=validate_join_event)
    @load_event()
    @require_event_is_joinable()
    @check_demographic_eligibility()
    @check_team_join_eligibility()
    @event_reg_namespace.doc(**JOIN_EVENT_DOC)
    def post(self, event_id):
        """Join an event by creating or joining a team"""
        result = join_event_controller()
        return success_response(result)


@event_reg_namespace.route("/create_registration_period")
class CreateRegistrationPeriod(Resource):
    @admin_endpoint(json_required=True, validation_func=validate_event_registration_creation)
    @load_event_from_request()
    @event_reg_namespace.doc(**CREATE_EVENT_REGISTRATION_DOC)
    def post(self):
        """Create event registration period"""
        data = g.validated_data
        result = create_event_registration(
            data.get("public", False),
            data.get("reg_open", False),
            data.get("reg_start_date"),
            data.get("reg_end_date"),
        )
        return success_response(result, status_code=201)
