from flask import Flask, Blueprint, request, jsonify, Response , g
from app.database.db import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import UserSchema, ValidationError
from sqlalchemy.orm import Session, Query
from app.utils.token_required import token_required 
from typing import Dict

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/v1/user")

@user_bp.route("/profile", methods=['GET'])
@token_required
def get_user() -> Response:
    try:
        current_user = g.current_user
        
        if not current_user:
            return jsonify({
                "error_code": True,
                "message": "User not found and unauthorized!",
                "data": None
            }), 400
            
        return jsonify({
            "error_code": False,
            "message": "User profile fetched successfully",
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error_code": True,
            "message": "Failed to fetch user profile!",
            "data": str(e)
        }), 500

    """User profile route and update route

    Returns:
        _type_: return json data 
    """

@user_bp.route("/updated", methods=['PUT'])
@token_required
def update_user() -> Response:
    session: Session = SessionLocal()
    user_schema: UserSchema = UserSchema()
    current_user: User = g.current_user
    
    try:
        data: Dict = request.get_json()
        if not data:
            return jsonify({"error_code": True, "message": "No data provided!", "data": []})
        
        if "password" in data and data.get("password"):
            return jsonify({
                "error_code": True,
                "message": "Password cannot be updated from this route.",
                "data": None
            })
        
        validation_data = user_schema.load(request.json, partial=True)
        
        for key, value in validation_data.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
               
        session.add(current_user)
        session.commit()
        
        return jsonify({
            "Error": False,
            "message": "Updated successfully.",
            "data": user_schema.dump(current_user)
        }), 200
        
    except ValidationError as VE:
        return jsonify({
            "error_code": True,
            "message": "Validation failed",
            "data": VE.messages
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            "error": True, 
            "message": "Update failed!", 
            "data": str(e)
        })
    finally:
        session.close()
        
        
           
