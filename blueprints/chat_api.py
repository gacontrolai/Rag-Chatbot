from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError as PydanticValidationError
from services.chat_service import ChatService
from services.workspace_service import WorkspaceService
from models.message import MessageCreate
from models.thread import ThreadCreate, ThreadUpdate
from models.workspace import WorkspaceCreate
from utils.exceptions import ValidationError, PermissionError, format_error_response
from extensions.limiter import limiter

chat_bp = Blueprint('chat', __name__, url_prefix='/v1')
chat_service = ChatService()
workspace_service = WorkspaceService()

# Workspace endpoints (focused on file management and RAG)
@chat_bp.route('/workspaces', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_workspace():
    """Create a new workspace for file management and RAG"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Request body is required'}}, 400
        
        workspace_data = WorkspaceCreate(**data)
        workspace = workspace_service.create_workspace(current_user_id, workspace_data)
        
        return {'workspace': workspace.dict()}, 201
        
    except PydanticValidationError as e:
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.errors()
            }
        }, 400
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while creating workspace'
            }
        }, 500

@chat_bp.route('/workspaces', methods=['GET'])
@jwt_required()
def get_workspaces():
    """Get user's workspaces"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        skip = (page - 1) * limit
        
        workspaces = workspace_service.get_user_workspaces(current_user_id, skip=skip, limit=limit)
        
        return {
            'workspaces': [ws.dict() for ws in workspaces],
            'page': page,
            'limit': limit
        }, 200
        
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching workspaces'
            }
        }, 500

@chat_bp.route('/workspaces/<workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace(workspace_id):
    """Get workspace by ID"""
    try:
        current_user_id = get_jwt_identity()
        workspace = workspace_service.get_workspace(workspace_id, current_user_id)
        
        if not workspace:
            return {'error': {'code': 'WORKSPACE_NOT_FOUND', 'message': 'Workspace not found'}}, 404
        
        return {'workspace': workspace.dict()}, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching workspace'
            }
        }, 500

@chat_bp.route('/workspaces/<workspace_id>/threads', methods=['GET'])
@jwt_required()
def get_workspace_threads(workspace_id):
    """Get threads that reference a specific workspace"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        skip = (page - 1) * limit
        
        threads = chat_service.get_workspace_threads(workspace_id, current_user_id, skip=skip, limit=limit)
        
        return {
            'threads': [thread.dict() for thread in threads],
            'page': page,
            'limit': limit,
            'workspace_id': workspace_id
        }, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching workspace threads'
            }
        }, 500

# Independent Thread endpoints
@chat_bp.route('/threads', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def create_thread():
    """Create a new independent chat thread (optionally with workspace reference)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        thread_data = ThreadCreate(**data)
        thread = chat_service.create_thread(current_user_id, thread_data)
        
        return {'thread': thread.dict()}, 201
        
    except PydanticValidationError as e:
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.errors()
            }
        }, 400
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while creating thread'
            }
        }, 500

@chat_bp.route('/threads', methods=['GET'])
@jwt_required()
def get_user_threads():
    """Get user's threads"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        skip = (page - 1) * limit
        
        threads = chat_service.get_user_threads(current_user_id, skip=skip, limit=limit)
        
        return {
            'threads': [thread.dict() for thread in threads],
            'page': page,
            'limit': limit
        }, 200
        
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching threads'
            }
        }, 500

@chat_bp.route('/threads/<thread_id>', methods=['GET'])
@jwt_required()
def get_thread(thread_id):
    """Get thread by ID"""
    try:
        current_user_id = get_jwt_identity()
        thread = chat_service.get_thread(thread_id, current_user_id)
        
        if not thread:
            return {'error': {'code': 'THREAD_NOT_FOUND', 'message': 'Thread not found'}}, 404
        
        return {'thread': thread.dict()}, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching thread'
            }
        }, 500

@chat_bp.route('/threads/<thread_id>', methods=['PATCH'])
@jwt_required()
def update_thread(thread_id):
    """Update thread (title, workspace reference, status)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Request body is required'}}, 400
        
        thread_update = ThreadUpdate(**data)
        
        # Convert to dict and remove None values
        update_data = {k: v for k, v in thread_update.dict().items() if v is not None}
        
        thread = chat_service.update_thread(thread_id, current_user_id, update_data)
        
        if not thread:
            return {'error': {'code': 'THREAD_NOT_FOUND', 'message': 'Thread not found'}}, 404
        
        return {'thread': thread.dict()}, 200
        
    except PydanticValidationError as e:
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.errors()
            }
        }, 400
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while updating thread'
            }
        }, 500

@chat_bp.route('/threads/<thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    """Delete thread"""
    try:
        current_user_id = get_jwt_identity()
        success = chat_service.delete_thread(thread_id, current_user_id)
        
        if not success:
            return {'error': {'code': 'THREAD_NOT_FOUND', 'message': 'Thread not found'}}, 404
        
        return {'message': 'Thread deleted successfully'}, 200
        
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while deleting thread'
            }
        }, 500

# Message endpoints
@chat_bp.route('/threads/<thread_id>/messages', methods=['POST'])
@jwt_required()
@limiter.limit("60 per hour")
def send_message(thread_id):
    """Send a message to the chatbot"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Request body is required'}}, 400
        
        message_data = MessageCreate(**data)
        message = chat_service.send_message(thread_id, current_user_id, message_data)
        
        return {'message': message.dict()}, 201
        
    except PydanticValidationError as e:
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.errors()
            }
        }, 400
    except ValidationError as e:
        return format_error_response(e, 400)
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while sending message'
            }
        }, 500

@chat_bp.route('/threads/<thread_id>/messages', methods=['GET'])
@jwt_required()
def get_thread_messages(thread_id):
    """Get messages in a thread"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        messages = chat_service.get_thread_messages(thread_id, current_user_id, skip=skip, limit=limit)
        
        return {
            'messages': [msg.dict() for msg in messages],
            'page': page,
            'limit': limit
        }, 200
        
    except ValidationError as e:
        return format_error_response(e, 400)
    except PermissionError as e:
        return format_error_response(e, 403)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching messages'
            }
        }, 500 