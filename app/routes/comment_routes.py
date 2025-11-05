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
     
        
@comment_bp.route("/get_by_post/<string:post_id>", methods=['GET'])
@token_required
def get_comments_by_post(post_id):
    session = SessionLocal()
    try:
        try:
            # Get query parameter for pagination(default: page=1, per_page=10)
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValidationError:
            return api_response(True, "Invalid request headers!", None, 400)

        # Join Comment and User tables
        comments = session.query(Comment, User).join(User, Comment.user_id == User.id).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at)).offset((page - 1)* per_page).limit(per_page).all()
        if not comments:
            return api_response(True, "No comments found for this post!", [], 404)
        
        result = []
        for comment, user in comments:
            result.append({
                "comment_id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at,
                "user": {
                    "user_id": str(user.id),
                    "username": user.username,
                    "email": user.email
                }
            })
        
        # Count total comments
        total_comments = session.query(Comment).filter(Comment.post_id == post_id).count()

        return api_response(False, "Fetched comments successfully.", {
            "comments_data": result,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_comments
            }
        }, 200)
    
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch comments", str(e), 500)
    finally:
        session.close()        
