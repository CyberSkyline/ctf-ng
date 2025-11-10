from flask_restx import Namespace, Resource
from ...core.middleware.auth import user_endpoint, public_endpoint
from ...core.utils import success_response, error_response
from ...core.middleware.loaders.load_sponsor import load_sponsor
from ...core.middleware.loaders import LoaderType
from ..models.Sponsor import Sponsor

sponsors_user_namespace = Namespace("/sponsors", description="user endpoints for sponsors")


@sponsors_user_namespace.route("")
class SponsorsUser(Resource):
    @public_endpoint()
    @sponsors_user_namespace.doc(
        description="Get all sponsors",
        responses={
            200: "Success",
            500: "Internal server error",
        },
    )
    def get(self, **kwargs):
        """Get all sponsors (user)"""

        sponsors = Sponsor.get_all_sponsors()
        return success_response(sponsors)

@sponsors_user_namespace.route("/<int:sponsor_id>")
class SponsorByIDUser(Resource):
    @public_endpoint()
    @load_sponsor(LoaderType.PARAM)
    @sponsors_user_namespace.doc(
        description="Get sponsor by ID",
        responses={
            200: "Success",
            404: "Sponsor not found",
            500: "Internal server error",
        },
)
    def get(self, sponsor_id, sponsor, **kwargs):
        """Get sponsor by ID (user)"""


        return success_response(sponsor)

@sponsors_user_namespace.route("/search")
class SponsorSearchUser(Resource):
    @user_endpoint(json_required=True)
    @sponsors_user_namespace.doc(
        description="Search for a sponsor by name",
        params={
            "name": {
                "description": "Name of the sponsor to search for",
                "required": True,
                "type": "string",
                "example": "Acme Corp"
            }
        },
        responses={
            200: "Success",
            404: "Sponsor not found",
            500: "Internal server error",
        },
    )
    def get(self, json_data, **kwargs):
        """Search for a sponsor by name (user)"""
        name = json_data.get("name")
        if not name:
            return error_response("Name parameter is required", "validation", 400)

        sponsors = Sponsor.search_by_name(name)
        if not sponsors:
            return error_response("Sponsor not found", "not_found", 404)

        return success_response(sponsors)