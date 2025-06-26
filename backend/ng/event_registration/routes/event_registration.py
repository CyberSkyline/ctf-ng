from flask_restx import Namespace, Resource, reqparse
from ...core.utils.logger import get_logger
from CTFd.utils.decorators import authed_only
from flask import g
from ...core.middleware import json_body_required, handle_integrity_error, authed_user_required
from ..controllers import join_event_new_team, join_event_existing_team, create_registration
from ..controllers.get_user_demographic import get_user_demographic
from ...core.utils.domain_validators import validate_join_event, validate_event_registration_creation
from CTFd.utils.decorators import admins_only

event_reg_namespace= Namespace("event_registration", description="Event Registration related operations")
logger = get_logger(__name__)
parser = reqparse.RequestParser()
parser.add_argument("event_id", type=int, required=True, help="The ID of the event to get demographics for")


@event_reg_namespace.route("")
class UserDemographics(Resource):
    @authed_only
    @handle_integrity_error
    @event_reg_namespace.doc(
        description="Get user demographics for an event",
        responses={
            200: "Success - User demographics retrieved",
            400: "Bad Request - Missing parameters or invalid data",
            403: "Forbidden - User not authenticated" ,
            404: "Not Found - User or event does not exist",
        }
    )
    def get(self):
        """Get user demographics for an event

        Returns:
            JSON: User demographics for the event or error message
        """
        id = g.user.id
        args = parser.parse_args()
        event_id = args.get("event_id")
        demographics = get_user_demographic(
            user_id=id,
            event_id=event_id
        )
        if not demographics["success"]:
            logger.warning(
                "Get user demographics failed",
                extra={"context": {"user_id": id, "event_id": event_id, "error": demographics["error"]}},
            )
            if demographics["error"] == "No demographic data found for user ID {} in event ID {}".format(id, event_id):
                return {"success": False, "error": demographics["error"]}, 404
            return {"success": False, "error": demographics["error"]}, 400
        
        return demographics, 200

@event_reg_namespace.route("/join_event")
class JoinEvent(Resource):

    @authed_only
    @authed_user_required
    @json_body_required
    @handle_integrity_error
    @event_reg_namespace.doc(
        description="Join an event",
        params={
            "event_id": "The ID of the event to join",
            "team_name": "The name of the new team to create (optional)",
            "invite_code": "The invite code for an existing team (optional)"
        },
        responses={
            200: "Success - User joined the event",
            400: "Bad Request - Missing parameters or error in joining",
            403: "Forbidden - User not authenticated",
            404: "Not Found - Event does not exist"
        }
    )
    def post(self):
        """Join an event"""

        user_id = g.user.id
        data = g.json_data

        event_id = data.get("event_id")
        team_name = data.get("team_name")
        invite_code = data.get("invite_code")

        is_valid, errors = validate_join_event(data)
        if not is_valid:
            logger.warning(
                "Join event failed - validation errors",
                extra={"context": {"event_id": event_id, "user_id": user_id, "errors": errors}},
            )
            return {"success": False, "error": errors}, 400


        if not event_id or not (team_name or invite_code):
            logger.warning(
                "Join event failed - missing required parameters",
                extra={"context": {"event_id": event_id, "user_id": user_id, "team_name": team_name, "invite_code": invite_code}},
            )
            return {
                "success": False,
                "error": "Missing required parameters: event_id and either team_name or invite_code are required."
            }, 400
        if invite_code:
            response = join_event_existing_team(event_id, user_id, invite_code)

            if not response["success"]:
                logger.warning(
                    "Join event failed - error in join_event_existing_team",
                    extra={"context": {"event_id": event_id, "user_id": user_id, "error": response["error"]}},
                )
                return response, 400

            return response, 200
            
        if team_name:
            response = join_event_new_team(event_id, user_id, team_name)

            if not response["success"]:
                logger.warning(
                    "Join event failed - error in join_event_new_team",
                    extra={"context": {"event_id": event_id, "user_id": user_id, "error": response["error"]}},
                )
                return response, 400
            return response, 200

@event_reg_namespace.route("/create_registration_period")
class CreateRegistrationPeriod(Resource):
    @authed_only
    @authed_user_required
    @admins_only
    @json_body_required
    @handle_integrity_error
    @event_reg_namespace.doc(
        description="Create a new event registration period",
        params={
            "event_id": "The ID of the event for which to create the registration period",
            "start_date": "The start date of the registration period (ISO format)",
            "end_date": "The end date of the registration period (ISO format)",
            "reg_open": "Whether the registration is open (boolean, default: False)",
            "public": "Whether the registration is public (boolean, default: False)"
        },
        responses={
            200: "Success - Registration period created",
            400: "Bad Request - Missing parameters or error in creation",
            403: "Forbidden - User not authenticated",
            404: "Not Found - Event does not exist"
        }
    )
    def post(self):
        """Create a new event registration period"""
        data = g.json_data
        event_id = data.get("event_id")
        start_date = data.get("start_date", None)
        end_date = data.get("end_date", None)
        reg_open = data.get("reg_open", False)
        public = data.get("public", False)


        is_valid, errors = validate_event_registration_creation(data)
        if not is_valid:
            logger.warning(
                "Create registration period failed - validation errors",
                extra={"context": {"event_id": event_id, "errors": errors}},
            )
            return {"success": False, "error": errors}, 400

        response = create_registration(event_id, public=public, reg_open=reg_open, reg_start_date=start_date, reg_end_date=end_date)

        if not response["success"]:
            logger.warning(
                "Create registration period failed - error in create_registration_period",
                extra={"context": {"event_id": event_id, "error": response["error"]}},
            )
            return {"success": False, "error": response["error"]}, 400

        return {
            "success": True,
            "event_registration": {
                "event_id": response["event_registration"].event_id,
                "public": response["event_registration"].public,
                "reg_open": response["event_registration"].reg_open,
                "reg_start_date": response["event_registration"].reg_start_date or None,
                "reg_end_date": response["event_registration"].reg_end_date or None
            }
        }, 200
