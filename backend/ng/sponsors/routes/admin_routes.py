from flask_restx import Namespace, Resource
from ..models.Sponsor import Sponsor
from ...core.utils import success_response
from ...core.middleware.auth import admin_endpoint
from ...core.middleware.loaders.load_sponsor import load_sponsor
from ...core.middleware.loaders import LoaderType

sponsors_admin_namespace = Namespace("/admin/sponsors", description="admin endpoints for managing sponsors")


@sponsors_admin_namespace.route("")
class SponsorsAdmin(Resource):
    @admin_endpoint()
    @sponsors_admin_namespace.doc(
        description="Get all sponsors",
        responses={
            200: "Success",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
    )
    def get(self, **kwargs):
        """Get all sponsors (admin only)"""
        sponsors = Sponsor.query.all()
        return success_response(sponsors)

    @admin_endpoint(json_required=True, validation_func=Sponsor.validate)
    @sponsors_admin_namespace.doc(
        description="Create a new sponsor",
        responses={
            201: "Sponsor created successfully",
            400: "Bad Request - Invalid input",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
        params={
            "name": {
                "description": "Name of the sponsor",
                "required": True,
                "type": "string",
                "example": "Acme Corp"
            },
            "logo": {
                "description": "URL of the sponsor's logo",
                "required": False,
                "type": "string",
                "example": "https://example.com/logo.png"
            }
        },
    )
    def post(self, validated_data, **kwargs):
        """Create a new sponsor (admin only)"""

        result = Sponsor.create_sponsor(**validated_data)

        return success_response(result, status_code=201)

@sponsors_admin_namespace.route("/<int:sponsor_id>")
class SponsorByIDAdmin(Resource):
    @admin_endpoint()
    @load_sponsor(LoaderType.PARAM)
    @sponsors_admin_namespace.doc(
        description="Get sponsor by ID",
        responses={
            200: "Success",
            403: "Forbidden - Admin access required",
            404: "Sponsor not found",
            500: "Internal server error",
        },
    )
    def get(self, sponsor_id, sponsor, **kwargs):
        """Get sponsor by ID (admin only)"""

        return success_response(sponsor)


    @admin_endpoint(json_required=True, validation_func=Sponsor.validate)
    @load_sponsor(source=LoaderType.PARAM)
    @sponsors_admin_namespace.doc(
        description="Update sponsor by ID",
        responses={
            200: "Sponsor updated successfully",
            400: "Bad Request - Invalid input",
            403: "Forbidden - Admin access required",
            404: "Sponsor not found",
            500: "Internal server error",
        },
    )
    def put(self, sponsor_id, sponsor, validated_data, **kwargs):
        """Update sponsor by ID (admin only)"""


        sponsor.update(**validated_data)

        return success_response(sponsor)