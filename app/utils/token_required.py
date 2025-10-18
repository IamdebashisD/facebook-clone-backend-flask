from flask import request, jsonify, g
from sqlalchemy.orm import Query
from functools import wraps
from app.database.db import SessionLocal
from .jwt_helper import decode_token
from app.models.user_model import User
from typing import Dict


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token: Dict = request.headers.get("Authorization")
        if not token:
            return jsonify({"error_code": True, "message": "Token is missing!"}), 401
        
        token: str = token.split(" ")[1]
        payload: Dict = decode_token(token)
          
        if not payload or payload.get("type") != "access":
            return jsonify({"error_code": True, "message": "Invalid or expired token!"}), 401 
        
        # create a session
        session = SessionLocal()
        try:
            user: Query = session.query(User).filter_by(id=payload['user_id']).first()
        
            if not user:
                return jsonify({"error_code": True, "message": "User not found"}), 404
        
            g.current_user = user
            
        finally:
            session.close()
            
        return f(*args, **kwargs)
    return decorated
