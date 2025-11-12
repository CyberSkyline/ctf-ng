from flask_restx import Namespace

fileuploads_namespace = Namespace('fileuploads', description='File upload operations')
from .public_files import fileuploads_namespace

__all__ = ['fileuploads_namespace']