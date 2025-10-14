from flask import Flask
from .database.db import Base, engine
from app.routes import all_blueprints

def create_app():
    app = Flask(__name__)
    
    Base.metadata.create_all(bind=engine)
    
    '''Register all blueprint here - '''
    for bp in all_blueprints:
        app.register_blueprint(bp)

    
    return app