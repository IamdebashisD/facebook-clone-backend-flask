from flask import Flask
from .database.db import Base, engine
from app.routes import all_blueprints


# --- FIX START ---
# IMPORT ALL YOUR MODELS HERE to ensure SQLAlchemy is aware of them 
# before calling create_all(). This resolves the "failed to locate a name ('Post')" error.
import app.models.user_model
import app.models.post_model
import app.models.like_model
import app.models.comment_model
import app.models.token_blacklist_model

def create_app():
    app = Flask(__name__)
    
    Base.metadata.create_all(bind=engine)
    
    '''Register all blueprint here - '''
    for bp in all_blueprints:
        app.register_blueprint(bp)

    
    return app