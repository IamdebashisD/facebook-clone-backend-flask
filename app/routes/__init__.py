from .ping_routes import ping_bp
from .auth_routes import auth_bp
from .user_routes import user_bp
from .post_routes import post_bp

all_blueprints = [ping_bp, auth_bp, user_bp, post_bp]

