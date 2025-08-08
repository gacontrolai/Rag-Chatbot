from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per day", "1000 per hour"]  # Very generous for testing
)

def init_limiter(app):
    """Initialize rate limiter"""
    limiter.init_app(app) 