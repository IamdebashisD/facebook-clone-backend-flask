from flask import Blueprint, request, Response, g
from app.database.db import SessionLocal
from app.models.comment_model import Comment
from app.models.user_model import User
from app.schemas.comment_schema import CommentSchema
from app.utils.response_helper import api_response
from app.utils.token_required import token_required
from datetime import datetime, timezone
from marshmallow import ValidationError
from sqlalchemy import desc

comment_bp = Blueprint("comment_bp", __name__, url_prefix="/api/v1/comments")

@comment_bp.route("/add", methods=['POST'])
@token_required
@token_required
def add_comment():    
    session = SessionLocal()
    comment_schema = CommentSchema()
    current_user = g.current_user
    
    try:
        data = request.get_json() or {}
        if not data or not data.get("post_id") or not data.get("content"):
            return api_response(True, "Post_id and Content are required!")
        
        # Validate and deserialized data
        validate_data =  comment_schema.load(data)
        
        new_comment = Comment(
            post_id = validate_data["post_id"],
            content = validate_data["content"],
            user_id = current_user.id
        )
        session.add(new_comment)
        session.commit()
        
        return api_response(False, "Comment added successfully", comment_schema.dump(new_comment), 201)

    except ValidationError as ve:
        return api_response(True, "Validation failed!", ve.messages, 400)

    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to add comment", str(e), 500)
    
    finally:
        session.close()
