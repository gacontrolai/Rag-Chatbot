from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from pydantic import ValidationError as PydanticValidationError
from services.auth_service import AuthService
from models.user import UserCreate, UserLogin
from utils.exceptions import ValidationError, AuthenticationError, format_error_response
from extensions.limiter import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/v1/auth')
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Request body is required'}}, 400
        
        # Validate input using Pydantic
        user_data = UserCreate(**data)
        
        # Register user
        user_response, tokens = auth_service.register_user(user_data)
        
        return {
            'user': user_response.dict(),
            'tokens': tokens
        }, 201
        
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
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred during registration'
            }
        }, 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return {'error': {'code': 'VALIDATION_ERROR', 'message': 'Request body is required'}}, 400
        
        # Validate input using Pydantic
        login_data = UserLogin(**data)
        
        # Login user
        user_response, tokens = auth_service.login_user(login_data)
        
        return {
            'user': user_response.dict(),
            'tokens': tokens
        }, 200
        
    except PydanticValidationError as e:
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': e.errors()
            }
        }, 400
    except AuthenticationError as e:
        return format_error_response(e, 401)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred during login'
            }
        }, 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        tokens = auth_service.refresh_token(current_user_id)
        
        return tokens, 200
        
    except AuthenticationError as e:
        return format_error_response(e, 401)
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred during token refresh'
            }
        }, 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return {
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }, 404
        
        return {'user': user.dict()}, 200
        
    except Exception as e:
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred while fetching user info'
            }
        }, 500 