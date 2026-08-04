"""
Admin API routes for certificates
"""

from flask_restx import Namespace, Resource

from ...core.utils import success_response
from ...core.middleware import admin_endpoint
from ..controllers import list_certificate_templates


certificates_admin_namespace = Namespace(
    "admin/certificates",
    description = "Admin certificate template operations"
)


@certificates_admin_namespace.route("")
class AllCertificateTemplates(Resource):
    @admin_endpoint()
    @certificates_admin_namespace.doc(
        description="List available certificate templates",
        responses={
            200: "Success - Returns list of available certificate templates",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            500: "Internal server error",
        },
    )
    def get(self, **kwargs):
        """
        Get all certificate templates
        """
        templates = list_certificate_templates()
        return success_response({"files": templates})
