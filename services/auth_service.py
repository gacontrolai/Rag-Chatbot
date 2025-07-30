import bcrypt
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Optional, Dict, Any, Tuple
from repositories.user_repo import UserRepository
from models.user import UserCreate, UserLogin, UserResponse, UserPlan
from utils.exceptions import ValidationError, AuthenticationError

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register_user(self, user_data: UserCreate) -> Tuple[UserResponse, Dict[str, str]]:
        """Register a new user and return user data with tokens"""
        # Hash password
        password_hash = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        print(password_hash)
        # Create user
        user_id = self.user_repo.create_user(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name
        )
        
        if not user_id:
            raise ValidationError("Email already exists")
        
        # Get created user
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise Exception("Failed to create user")
        
        # Generate tokens
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        # Convert to response model
        user_response = UserResponse(
            id=user['id'],
            email=user['email'],
            name=user['name'],
            plan=user['plan'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        )
        
        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
        return user_response, tokens
    
    def login_user(self, login_data: UserLogin) -> Tuple[UserResponse, Dict[str, str]]:
        """Login user and return user data with tokens"""
        # Find user by email
        user = self.user_repo.find_by_email(login_data.email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not bcrypt.checkpw(
            login_data.password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        ):
            raise AuthenticationError("Invalid email or password")
        
        # Generate tokens
        access_token = create_access_token(identity=user['id'])
        refresh_token = create_refresh_token(identity=user['id'])
        
        # Convert to response model
        user_response = UserResponse(
            id=user['id'],
            email=user['email'],
            name=user['name'],
            plan=user['plan'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        )
        
        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
        return user_response, tokens
    
    def refresh_token(self, user_id: str) -> Dict[str, str]:
        """Generate new access token"""
        # Verify user still exists
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        access_token = create_access_token(identity=user_id)
        
        return {
            'access_token': access_token
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            name=user['name'],
            plan=user['plan'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        )
    
    def verify_user_exists(self, user_id: str) -> bool:
        """Verify if user exists"""
        user = self.user_repo.find_by_id(user_id)
        return user is not None 