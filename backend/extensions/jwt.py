from flask_jwt_extended import JWTManager
from datetime import timedelta

jwt = JWTManager()

def init_jwt(app):
    """Initialize JWT extension"""
    app.config['JWT_SECRET_KEY'] = app.config['JWT_SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    
    jwt.init_app(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': 'Token has expired'
            }
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid token'
            }
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'error': {
                'code': 'TOKEN_REQUIRED',
                'message': 'Access token is required'
            }
        }, 401 