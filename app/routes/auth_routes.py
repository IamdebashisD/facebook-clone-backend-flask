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
from app.utils.email_helper import send_welcome_message


'''create Blueprint'''
auth_bp = Blueprint("auth_bp", __name__ , url_prefix="/api/v1/auth")


user_schema: UserSchema = UserSchema()          # Initialize schema 

@auth_bp.route("/register", methods=['POST'])
def register() -> Response:
    session: Session = SessionLocal()               # Initialize db
    try:
        data: Dict = request.get_json() or {}
        if not data or not data.get("username") or not data.get("email") or not data.get("password"):
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
            return api_response(True, "Username or email already exists", None, 400)
            
        # Create new user instance
        new_user: User = User(**validate_input)
        session.add(new_user)
        session.commit()
                
        # Send welcome message
        try:
            send_welcome_message(new_user.email, new_user.username)
            print("Email sent successfully.")
        except Exception as e:
            print(f"Email sending failed: {str(e)}")

        return jsonify({
            "error_code": False,
            "message": "User registered successfully",
            "success": True,
        }), 201

    except Exception as e:
        session.rollback()
        return api_response(True, "Registration Failed!", str(e), 500)
    finally:
        session.close()
        
        
'''<------  Login Route  ------>'''

@auth_bp.route("/login", methods=['POST'])
def login() -> Response:
    session: Session = SessionLocal()               # Initialize db
    try:
        data: Dict = request.get_json() or {}
        
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
    session: Session = SessionLocal()
    try:
        data: Dict = request.get_json() or {}
        
        if not data or not data.get("refresh_token"):
            return jsonify({
                "error_code": True, 
                "message": "Refresh token is required", 
                "data": None
            })

        refresh_token = data.get("refresh_token")
        # Decode the refresh token
        payload: Dict = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return jsonify({"error_code": True, "message": "Invalid refresh token"}), 401
        
        # Check if token is blacklisted
        blacklisted = session.query(TokenBlacklist).filter_by(token=refresh_token).first()
        if blacklisted:
            return jsonify({
                "error_code": True,
                "message": "Refresh token has been revoked or blacklisted",
                "data": None
            }), 401
        
        # Verify that the user still exists
        user = session.query(User).filter_by(id=payload["user_id"]).first()
        if not user:
            return api_response(True, "User not found or deleted", None, 404)
        
        # (Optional) verify token belongs to same user
        if str(user.id) != str(payload["user_id"]):
            return api_response(True, "Token does not belong to this user", 401)
            
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
    finally:
        session.close()



"""
    Route for log out
"""
@auth_bp.route("/logout", methods=['POST'])
@token_required
def logout():
    session = SessionLocal()
    current_user = g.current_user
    try:
        '''
            Handle access token from headers
        '''
        access_token = request.headers.get('Authorization')
        if not access_token:
            return api_response(True, "Access token is missing", [], 401)
            
        access_token = access_token.split(" ")[1] if " " in access_token else access_token
        
        # Decode the access token
        decode_access: dict = decode_token(access_token)
        if not decode_access or decode_access.get("type") != "access":
            return api_response(True, "Invalid access token!", 401)
        
        token_type_access = decode_access.get("type", "access")
        exp_timestamp = decode_access.get("exp")
        expires_access = datetime.datetime.fromtimestamp(exp_timestamp, datetime.timezone.utc)
        
        # Checking if token already exists or not
        exist_access_token = session.query(TokenBlacklist).filter_by(token = access_token).first()
        if exist_access_token:
            return api_response(True, "Access token already blacklisted", [], 401)
        
        # add to TokenBlacklist
        blacklisted_access_token = TokenBlacklist(
            token = access_token,
            token_type = token_type_access,
            user_id = str(current_user.id),
            expires_at = expires_access,
            reason = "logout"
        )        
        session.add(blacklisted_access_token)
        
        
        ''' 
            Handle refresh token from body
        '''
        data = request.get_json() or {}
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return api_response(True, "Refresh token is missing!", [], 401)
        
        # Decode the refresh token
        decode_refresh: dict = decode_token(refresh_token)
        if not decode_refresh or decode_refresh.get("type") != "refresh":
            return api_response(True, "Invalid refresh token!", 401)
        
        token_type_refresh = decode_refresh.get("type", "refresh")
        exp_timestamp = decode_refresh.get("exp")
        expires_refresh = datetime.datetime.fromtimestamp(exp_timestamp, datetime.timezone.utc)
        
        # Checking if token already exists or not
        exist_refresh_token =  session.query(TokenBlacklist).filter_by(token = refresh_token).first()
        if exist_refresh_token:
            return api_response(True, "Refresh token already blacklisted", [], 401)
        
        # add to TokenBlacklist
        blacklisted_refresh_token = TokenBlacklist(
            token = refresh_token,
            token_type = token_type_refresh,
            user_id = str(current_user.id),
            expires_at = expires_refresh,
            reason = "logout"
        )
        session.add(blacklisted_refresh_token)
        
        session.commit()
        return api_response(False, "User logged out successfully, Both tokens revoked", [], 200)
    
    except Exception as e:
        session.rollback()
        return api_response(True, "Logout failed", str(e), 500)

    finally:
        session.close()
