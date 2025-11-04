"""
My User API routes
"""
from CTFd.models import Users
from CTFd.utils.crypto import verify_password
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac
from flask_restx import Namespace, Resource
from flask import session
from ...core.utils import success_response
from ...core.middleware import (
    user_endpoint,
    public_endpoint,
)
from ...sponsors.models.Sponsor import Sponsor

users_user_namespace = Namespace("/users", description="user endpoints for users")


@users_user_namespace.route("/me")
class UserProfile(Resource):
    @user_endpoint()
    @users_user_namespace.doc(
        description="Get my user information",
        responses={
            200: "Success",
            401: "Unauthorized - Authentication required",
            404: "User not found",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """Get my user information"""
        return success_response(current_user)

@users_user_namespace.route("/me/events")
class UserEvents(Resource):
    @user_endpoint()
    @users_user_namespace.doc(
        description="Get my events",
        responses={
            200: "Success",
            401: "Unauthorized - Authentication required",
            404: "Events not found",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """Get my events"""
        events = current_user.get_events()
        return success_response(events)

@users_user_namespace.route("/me/teams")
class UserTeams(Resource):
    @user_endpoint()
    @users_user_namespace.doc(
        description="Get my teams",
        responses={
            200: "Success",
            404: "Teams not found",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """Get my teams"""
        teams = current_user.get_teams()
        return success_response(teams)

@users_user_namespace.route("/me/sponsor")
class UserSponsor(Resource):
    @user_endpoint()
    @users_user_namespace.doc(
        description="Get my sponsor information",
        responses={
            200: "Success",
            404: "Sponsor not found",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
    )
    def get(self, current_user, **kwargs):
        """Get my sponsor information"""


        return success_response(current_user.get_sponsor())

    @user_endpoint(json_required=True)
    @users_user_namespace.doc(
        description="Update my sponsor information",
        responses={
            200: "Sponsor updated successfully",
            400: "Bad Request - Invalid input",
            404: "Sponsor not found",
            401: "Unauthorized - Authentication required",
            500: "Internal server error",
        },
        params={
            "sponsor": {
                "description": "Sponsor name to associate with user",
                "in": "body",
                "required": True,
                "type": "string",
                "example": "Acme Corp"
            }
        },

    )
    def put(self, current_user, json_data, **kwargs):
        """Update my sponsor information"""

        sponsor_id = json_data.get("sponsor_id")
        if not sponsor_id:
            return {"success": False, "errors": {"sponsor": "Sponsor data is required"}}, 400

        sponsor = Sponsor.find_by_id(sponsor_id)
        if not sponsor:
            return {"success": False, "errors": {"sponsor": "Sponsor not found"}}, 404

        current_user.set_sponsor(sponsor)

        return success_response(sponsor)


#The POST request for login must have a nonce attached to it or it will be blocked by CSRF protection in many cases
@users_user_namespace.route("/login")
class UserLogin(Resource):
    @public_endpoint(json_required=True)
    @users_user_namespace.doc(
        description="User login endpoint",
        responses={
            200: "Login successful",
            401: "Unauthorized - Invalid credentials",
            500: "Internal server error",
        },
    )
    def post(self, json_data, **kwargs):
        """User login endpoint"""
        username = json_data.get("username")
        password = json_data.get("password")


        user = Users.query.filter_by(name=username).first()
        if not user:
            user = Users.query.filter_by(email=username).first()

        if user:
            if user.password is None:
                return {"success": False, "errors": {"authentication": "Invalid username or password"}}, 401

            if user and verify_password(password, user.password):
                session['id'] = user.id
                session['nonce'] = generate_nonce()
                session['hash'] = hmac(user.password)
                session['permanent'] = True

                return {"success": True}, 200
            else:
                return {"success": False, "errors": {"authentication": "Invalid username or password"}}, 401

        else:
            return {"success": False, "errors": {"authentication": "Invalid username or password"}}, 401



@users_user_namespace.route("/logout")
class UserLogout(Resource):
    @user_endpoint()
    @users_user_namespace.doc(
        description="User logout endpoint",
        responses={
            200: "Logout successful",
            401: "Unauthorized - Invalid credentials",
            500: "Internal server error",
        },
    )
    def post(self, current_user, **kwargs):
        """User logout endpoint"""

        session.clear()

        return {"success": True}, 200
