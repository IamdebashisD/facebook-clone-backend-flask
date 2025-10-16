from flask import Blueprint, request, jsonify, Response
from sqlalchemy.orm import Session, Query
from app.database.db import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import UserSchema

'''create Blueprint'''
auth_bp = Blueprint("auth_bp", __name__ , url_prefix="/api/auth")


user_schema: UserSchema = UserSchema()          # Initialize schema 
session: Session = SessionLocal()               # Initialize db

@auth_bp.route("/register", methods=['POST'])
def register() -> Response:
    try:
        data: dict = request.get_json()
        if not data:
            return jsonify({
                "error_code": True, 
                "message": "Invalid JSON data!", 
                "data": None
            }), 400
            
        # Validate & deserialize input
        validate_input: dict = user_schema.load(data)
        
        existing_user: Query = session.query(User).filter(User.email == data['email'] or User.username == data['username']).first()
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
        return ({
            "error_code": True,
            "message": "Registration failed",
            "data": str(e)
        }), 500
        
    finally:
        session.close()
