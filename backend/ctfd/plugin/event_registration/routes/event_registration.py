from flask_restx import Namespace, Resource, reqparse
from ...utils.logger import get_logger
from CTFd.utils.decorators import authed_only
from ...utils.decorators import json_body_required, handle_integrity_error
from ..controllers import join_event_new_team, join_event_existing_team
from ..controllers.get_user_demographic import get_user_demographic
from ...utils import get_current_user_id

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
        id = get_current_user_id()
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
            return demographics, 400
        
        return demographics, 200

@event_reg_namespace.route("/join_event")
class JoinEvent(Resource):

    @authed_only
    @json_body_required
    @handle_integrity_error
    @event_reg_namespace.doc(
        description="Join an event",
        responses={
            200: "Success - User joined the event",
            400: "Bad Request - Missing parameters or error in joining",
            403: "Forbidden - User not authenticated",
            404: "Not Found - Event does not exist"
        }
    )
    def post(self):
        """Join an event"""

        user_id = get_current_user_id()
        data = g.json_data

        event_id = data.get("event_id")
        team_name = data.get("team_name")
        invite_code = data.get("invite_code")


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
