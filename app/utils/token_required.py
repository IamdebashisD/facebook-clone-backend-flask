from flask import request, jsonify, g
from sqlalchemy.orm import Query
from functools import wraps
from app.database.db import SessionLocal
from .jwt_helper import decode_token
from app.models.user_model import User
from typing import Dict
from app.models.token_blacklist_model import TokenBlacklist
from app.utils.response_helper import api_response


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token: Dict = request.headers.get("Authorization")
        if not token:
            return jsonify({"error_code": True, "message": "Token is missing!"}), 401
        
        token: str = token.split(" ")[1] if " " in token else token
        
        # create a session
        session = SessionLocal()
        try:
            blacklisted = session.query(TokenBlacklist).filter_by(token=token).first()
            if blacklisted:
                return api_response(True, "Token has been blacklisted!", [], 401)
            
            payload: Dict = decode_token(token)
            if not payload or payload.get("type") != "access":
                return jsonify({"error_code": True, "message": "Invalid or expired token!"}), 401
            
            user_id = payload.get("user_id")
            if not user_id:
                return api_response(True, "Invalid token payload!", [], 400)
            
            user: Query = session.query(User).filter_by(id=user_id).first()
            if not user:
                return api_response(True, "User not found", [], 404)
                    
            g.current_user = user
            
        finally:
            session.close()
            
        return f(*args, **kwargs)
    return decorated
