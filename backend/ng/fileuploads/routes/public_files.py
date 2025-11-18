from flask_restx import Namespace, Resource
from flask import request
from ..controllers.public_files import (
    generate_upload_url,
    get_public_file,
    list_public_files,
    search_public_files,
    direct_upload_file
)

fileuploads_namespace = Namespace('fileuploads', description='File upload operations')



@fileuploads_namespace.route('/upload/url')
class FileUploadURL(Resource):
    @fileuploads_namespace.doc(
        description='Generate a presigned URL for direct client-side upload to S3',
        params={
            'folder': {
                'description': 'Target folder (sponsor-logos, event-cards, favicons)',
                'type': 'string',
                'enum': ['sponsor-logos', 'event-cards', 'favicons'],
                'required': True,
                'in': 'body',
                'example': 'sponsor-logos'
            },
            'content_type': {
                'description': 'MIME type of the file',
                'type': 'string',
                'required': True,
                'in': 'body',
                'example': 'image/png'
            }
        },
        responses={
            200: 'Success - Returns presigned URL and upload details',
            400: 'Bad Request - Invalid folder or content type',
            500: 'Internal Server Error',
            503: 'Service Unavailable - S3 storage not configured'
        }
    )
    def post(self):
        """Generate presigned URL for client-side upload

        This endpoint generates a presigned URL that allows clients to upload files
        directly to S3 without going through the server. Supports sponsor logos,
        event cards, and favicon uploads.
        """
        data = request.get_json()
        if not data:
            return {"error": "JSON data required"}, 400

        folder = data.get('folder')
        content_type = data.get('content_type')

        if not folder:
            return {"error": "Folder is required"}, 400
        if not content_type:
            return {"error": "Content type is required"}, 400

        return generate_upload_url({
            'folder': folder,
            'content_type': content_type
        })


@fileuploads_namespace.route('/list')
class FileList(Resource):
    @fileuploads_namespace.doc(
        description='List all files in a specified public folder',
        params={
            'folder': {
                'description': 'Folder name to list files from',
                'type': 'string',
                'enum': ['sponsor-logos', 'event-cards', 'favicons'],
                'required': True,
                'example': 'sponsor-logos'
            }
        },
        responses={
            200: 'Success - Returns list of files in the folder',
            400: 'Bad Request - Invalid or missing folder parameter',
            500: 'Internal Server Error',
            503: 'Service Unavailable - S3 storage not configured'
        }
    )
    def get(self):
        """List files in a public folder

        Retrieve a list of all files in the specified public folder.
        Returns file metadata including size, last modified date, and S3 key.
        """
        folder = request.args.get('folder')
        if not folder:
            return {"error": "Folder parameter is required"}, 400

        return list_public_files({
            'folder': folder
        })


@fileuploads_namespace.route('/file')
class FileAccess(Resource):
    @fileuploads_namespace.doc(
        description='Get a presigned download URL for a specific file',
        params={
            'folder': {
                'description': 'Folder containing the file',
                'type': 'string',
                'enum': ['sponsor-logos', 'event-cards', 'favicons'],
                'required': True,
                'example': 'sponsor-logos'
            },
            'filename': {
                'description': 'Name of the file to access',
                'type': 'string',
                'required': True,
                'example': 'abc123def456.png'
            }
        },
        responses={
            200: 'Success - Returns presigned download URL',
            400: 'Bad Request - Missing folder or filename parameter',
            404: 'Not Found - File does not exist',
            500: 'Internal Server Error',
            503: 'Service Unavailable - S3 storage not configured'
        }
    )
    def get(self):
        """Get presigned URL for file access

        Generate a presigned download URL for a specific file in a public folder.
        The URL is valid for 24 hours and allows direct access to the file.
        """
        folder = request.args.get('folder')
        filename = request.args.get('filename')

        if not folder:
            return {"error": "Folder parameter is required"}, 400
        if not filename:
            return {"error": "Filename parameter is required"}, 400

        return get_public_file({
            'folder': folder,
            'filename': filename
        })


@fileuploads_namespace.route('/search')
class FileSearch(Resource):
    @fileuploads_namespace.doc(
        description='Search for files across folders or within a specific folder',
        params={
            'folder': {
                'description': 'Specific folder to search in (optional)',
                'type': 'string',
                'enum': ['sponsor-logos', 'event-cards', 'favicons'],
                'required': False,
                'example': 'sponsor-logos'
            },
            'filename': {
                'description': 'Filename pattern to search for (optional)',
                'type': 'string',
                'required': False,
                'example': 'logo'
            },
            'limit': {
                'description': 'Maximum number of results to return',
                'type': 'integer',
                'required': False,
                'default': 10,
                'minimum': 1,
                'maximum': 50,
                'example': 10
            }
        },
        responses={
            200: 'Success - Returns search results',
            400: 'Bad Request - Invalid search parameters',
            500: 'Internal Server Error',
            503: 'Service Unavailable - S3 storage not configured'
        }
    )
    def get(self):
        """Search files across folders or within specific folder

        Flexible file search supporting multiple modes:
        - List all files in a folder (provide folder parameter only)
        - Search by filename pattern across all folders (provide filename parameter only)
        - Search by filename pattern within specific folder (provide both parameters)

        Results are limited to 50 maximum and sorted by filename.
        """
        return search_public_files()


@fileuploads_namespace.route('/upload/direct')
class DirectFileUpload(Resource):
    @fileuploads_namespace.doc(
        description='Upload a file directly to S3 (server-side upload with automatic presigned URL generation)',
        params={
            'folder': {
                'description': 'Target folder for the upload',
                'type': 'string',
                'enum': ['sponsor-logos', 'event-cards', 'favicons'],
                'required': True,
                'in': 'formData',
                'example': 'sponsor-logos'
            },
            'file': {
                'description': 'File to upload',
                'type': 'file',
                'required': True,
                'in': 'formData'
            }
        },
        responses={
            200: 'Success - File uploaded successfully',
            400: 'Bad Request - Invalid folder, missing file, or unsupported content type',
            500: 'Internal Server Error - Upload failed',
            503: 'Service Unavailable - S3 storage not configured'
        },
        consumes=['multipart/form-data']
    )
    def post(self):
        """Upload a file directly to S3 using presigned URLs

        This endpoint handles server-side file upload by:
        1. Validating the file and folder
        2. Generating a presigned upload URL
        3. Uploading the file to S3
        4. Returning file metadata

        Supports image files in sponsor-logos, event-cards, and favicons folders.
        """
        folder = request.form.get('folder')
        file = request.files.get('file')

        return direct_upload_file({
            'folder': folder,
            'file': file
        })
