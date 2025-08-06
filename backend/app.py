import os
from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import config
from extensions.db import init_db
from extensions.jwt import init_jwt
from extensions.limiter import init_limiter
from extensions.storage import init_storage
from extensions.logger import init_logger
from blueprints.auth_api import auth_bp
from blueprints.chat_api import chat_bp
from blueprints.file_api import file_bp

from pymongo import MongoClient

def create_app(config_name=None):
    """Flask application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    print("Initializing db")
    init_db(app)
    print("Initializing jwt")
    init_jwt(app)
    print("Initializing limiter")
    init_limiter(app)
    print("Initializing storage")
    init_storage(app)
    print("Initializing logger")
    init_logger(app)
    
    # Configure CORS properly for separate server deployment
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, 
         origins=cors_origins,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
         supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(file_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'AI Chatbot API'}, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'The method is not allowed for this endpoint'
            }
        }, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An internal server error occurred'
            }
        }, 500
    
    # Setup database indexes on first run
    with app.app_context():
        try:
            from repositories.user_repo import UserRepository
            from repositories.workspace_repo import WorkspaceRepository
            from repositories.thread_repo import ThreadRepository
            from repositories.message_repo import MessageRepository
            from repositories.file_repo import FileRepository
            
            # Create indexes
            UserRepository().create_indexes()
            WorkspaceRepository().create_indexes()
            ThreadRepository().create_indexes()
            MessageRepository().create_indexes()
            FileRepository().create_indexes()
            
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Warning: Could not create database indexes: {e}")
    
    return app

def create_production_app():
    """Create production app instance"""
    return create_app('production')

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 