from flask import Blueprint, request, jsonify, Response, g
from sqlalchemy import or_
from sqlalchemy.orm import Session, Query
from app.database.db import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import UserSchema
from typing import Dict, Any
from app.utils.jwt_helper import create_access_token, create_refresh_token, decode_token
from app.utils.token_required import token_required
from app.models.token_blacklist_model import TokenBlacklist
import datetime
from app.utils.response_helper import api_response


'''create Blueprint'''
auth_bp = Blueprint("auth_bp", __name__ , url_prefix="/api/v1/auth")


user_schema: UserSchema = UserSchema()          # Initialize schema 

@auth_bp.route("/register", methods=['POST'])
def register() -> Response:
    session: Session = SessionLocal()               # Initialize db
    try:
        data: Dict = request.get_json()
        if not data:
            return jsonify({
                "error_code": True, 
                "message": "Invalid JSON data!", 
                "data": None
            }), 400
            
        # Validate & deserialize input
        validate_input: Dict = user_schema.load(data)

        existing_user: Query = session.query(User).filter(
            or_(User.email == validate_input['email'], User.username == validate_input['username'])
        ).first()
        
        if existing_user:
            return jsonify({
                "error_code": True,
                "message": "Username or email already exists",
                "data": None
            }), 400
            
        # Create new user instance
        new_user: User = User(**validate_input)
        session.add(new_user)
        session.commit()
        
        return jsonify({
            "error_code": False,
            "message": "User registered successfully",
            "data": user_schema.dump(new_user),
        }), 201

    except Exception as e:
        return jsonify({
            "error_code": True,
            "message": "Registration failed",
            "data": str(e)
        }), 500
        
    finally:
        session.close()
        
        
'''<------  Login Route  ------>'''

@auth_bp.route("/login", methods=['POST'])
def login() -> Response:
    session: Session = SessionLocal()               # Initialize db
    try:
        data: Dict = request.get_json()
        
        # check if JSON is provided
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({
                "error_code": True,
                "message": "Email and Password are required",
                "data": None
            }), 400
        
        # create a Session
        user: Query = session.query(User).filter_by(email=data['email']).first()
        
        if not user or not user.verify_password(data["password"]):
            return jsonify({
                "error_code": True,
                "message": "Invalid email or password",
                "data": None
            }), 401

        # Generate access and refresh tokens
        access_token = create_access_token({"user_id": user.id, "email": user.email})
        refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})
        
        return jsonify({
            "error_code": False,
            "message": "Login successful",
            "data": {
                "user":{
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
        }), 200
            
    except Exception as e:
        return jsonify({
            "error_code": True,
            "message": "Login Failed! Please try again.",
            "data": str(e)
        }), 500
    finally:
        session.close()
        

# ------ Route refresh token -------- 
@auth_bp.route("/refresh", methods=['POST'])
def refresh_token() -> Response:
    try:
        data: Dict = request.get_json()
        
        if not data or not data.get("refresh_token"):
            return jsonify({
                "error_code": True, 
                "message": "Refresh token is required", 
                "data": None
            })

        refresh_token = data.get("refresh_token")
        payload: Dict = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return jsonify({"error_code": True, "message": "Invalid refresh token"}), 401
        
        new_access_token = create_access_token({
            "user_id": payload['user_id'], "email": payload['email']
        })
        
        return jsonify({
            "error_code": False,
            "message": "Access token refreshed successfully",
            "data": {"access_token": new_access_token, "token_type": "Bearer"}
        }), 200
        
    except Exception as e:
        return jsonify({
            "error_code":True,
            "message": "Failed to refresh token",
            "data": str(e)
        }), 500


        
"""
    Route for log out
"""
@auth_bp.route("/logout", methods=['POST'])
@token_required
def logout():
    session = SessionLocal()
    current_user = g.current_user
    try:
        token = request.headers.get('Authorization')
        if not token:
            return api_response(True, "Token is missing", [], 401)
            
        token = token.split(" ")[1] if " " in token else token
        
        payload: dict = decode_token(token)
        token_type = payload.get("type", "access")
        exp_timestamp = payload.get("exp")
        expires_at = datetime.datetime.utcfromtimestamp(exp_timestamp)
        
        '''add to TokenBlacklist'''
        blacklisted_token = TokenBlacklist(
            token = token,
            user_id = str(current_user.id),
            token_type = token_type,
            expires_at = expires_at,
            reason = "logout"
        )        
        session.add(blacklisted_token)
        session.commit()
        return api_response(False, "User logged out successfully", [], 200)
    
    except Exception as e:
        session.rollback()
        return api_response(True, "Logout failed", str(e), 500)

    finally:
        session.close()
