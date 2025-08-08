from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError as PydanticValidationError
from werkzeug.utils import secure_filename
from services.file_service import FileService
from models.file import FileUpload
from utils.exceptions import ValidationError, PermissionError, format_error_response
from extensions.limiter import limiter

file_bp = Blueprint('files', __name__, url_prefix='/v1')
file_service = FileService()

@file_bp.route('/workspaces/<workspace_id>/files', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def upload_file(workspace_id):
    """Upload a file to workspace with content extraction and embedding"""
    try:
        current_user_id = get_jwt_identity()
        print(f"Upload request from user {current_user_id} for workspace {workspace_id}")
        
        # Check if file is in request
        if 'file' not in request.files:
            print("Error: No file provided in request")
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'No file provided'}}, 400
        
        file = request.files['file']
        if file.filename == '':
            print("Error: No file selected")
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'No file selected'}}, 400
        
        print(f"File uploaded: {file.filename}")
        
        # Get optional file metadata from form data
        file_data = None
        if request.form.get('title'):
            try:
                file_data = FileUpload(title=request.form.get('title'))
            except PydanticValidationError as e:
                return {
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid file metadata',
                        'details': e.errors()
                    }
                }, 400
        
        # Upload and process file
        file_response = file_service.upload_file(workspace_id, current_user_id, file, file_data)
        
        return {
            'file': file_response.dict(),
            'message': 'File uploaded successfully. Content extraction and embedding in progress.'
        }, 201
        
    except ValidationError as e:
        return format_error_response(e, 400)
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'An error occurred while uploading file: {str(e)}'
            }
        }, 500

@file_bp.route('/workspaces/<workspace_id>/files', methods=['GET'])
@jwt_required()
def get_workspace_files(workspace_id):
    """Get files in a workspace"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        skip = (page - 1) * limit
        
        files = file_service.get_workspace_files(workspace_id, current_user_id, skip=skip, limit=limit)
        
        return {
            'files': [file.dict() for file in files],
            'page': page,
            'limit': limit,
            'total': len(files)
        }, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching files'
            }
        }, 500

@file_bp.route('/files/<file_id>', methods=['GET'])
@jwt_required()
def get_file_details(file_id):
    """Get detailed file information"""
    try:
        current_user_id = get_jwt_identity()
        file_details = file_service.get_file_details(file_id, current_user_id)
        
        if not file_details:
            return {'error': {'code': 'FILE_NOT_FOUND', 'message': 'File not found'}}, 404
        
        return {'file': file_details.dict()}, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching file details'
            }
        }, 500

@file_bp.route('/files/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a file"""
    try:
        current_user_id = get_jwt_identity()
        success = file_service.delete_file(file_id, current_user_id)
        
        if not success:
            return {'error': {'code': 'FILE_NOT_FOUND', 'message': 'File not found'}}, 404
        
        return {'message': 'File deleted successfully'}, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while deleting file'
            }
        }, 500

@file_bp.route('/workspaces/<workspace_id>/files/search', methods=['POST'])
@jwt_required()
@limiter.limit("50 per hour")
def search_files(workspace_id):
    """Search files in workspace using semantic similarity"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Search query is required'}}, 400
        
        query = data['query'].strip()
        if not query:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Search query cannot be empty'}}, 400
        
        top_k = data.get('top_k', 5)
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'top_k must be between 1 and 20'}}, 400
        
        # Perform search
        results = file_service.search_files(workspace_id, current_user_id, query, top_k)
        
        return {
            'results': results,
            'query': query,
            'total_results': len(results)
        }, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while searching files'
            }
        }, 500

@file_bp.route('/workspaces/<workspace_id>/files/supported-formats', methods=['GET'])
@jwt_required()
def get_supported_formats(workspace_id):
    """Get list of supported file formats"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify workspace access
        from repositories.workspace_repo import WorkspaceRepository
        workspace_repo = WorkspaceRepository()
        if not workspace_repo.is_member(workspace_id, current_user_id):
            raise PermissionError("Access denied to workspace")
        
        return {
            'supported_formats': ['.txt', '.csv', '.docx'],
            'max_file_size': '50MB',
            'features': {
                'content_extraction': True,
                'text_embedding': True,
                'semantic_search': True
            }
        }, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching supported formats'
            }
        }, 500

@file_bp.route('/vector-store/stats', methods=['GET'])
@jwt_required()
def get_vector_store_stats():
    """Get vector store statistics and configuration"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get vector store statistics
        stats = file_service.get_vector_stats()
        
        return {
            'vector_store_stats': stats,
            'message': 'Vector store statistics retrieved successfully'
        }, 200
        
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'An error occurred while fetching vector store stats: {str(e)}'
            }
        }, 500 