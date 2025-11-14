from flask_restx import Resource
from flask import request
from ..controllers.public_files import (
    generate_upload_url,
    get_public_file,
    list_public_files,
    search_public_files,
    direct_upload_file
)

from . import fileuploads_namespace

@fileuploads_namespace.route('/upload/url')
class FileUploadURL(Resource):
    def post(self):
        """Generate presigned URL for client-side upload"""
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
    def get(self):
        """List files in a public folder"""
        folder = request.args.get('folder')
        if not folder:
            return {"error": "Folder parameter is required"}, 400

        return list_public_files({
            'folder': folder
        })


@fileuploads_namespace.route('/file')
class FileAccess(Resource):
    def get(self):
        """Get presigned URL for file access"""
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
    def get(self):
        """Search files across folders or within specific folder"""
        return search_public_files()


@fileuploads_namespace.route('/upload/direct')
class DirectFileUpload(Resource):
    def post(self):
        """Upload a file directly to S3 using presigned URLs"""
        folder = request.form.get('folder')
        file = request.files.get('file')

        return direct_upload_file({
            'folder': folder,
            'file': file
        })
