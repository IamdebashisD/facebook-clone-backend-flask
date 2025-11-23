from flask import Blueprint, request, Response, g
from app.database.db import SessionLocal
from app.models.comment_model import Comment
from app.models.user_model import User
from app.models.post_model import Post
from app.schemas.comment_schema import CommentSchema
from app.utils.response_helper import api_response
from app.utils.token_required import token_required
from datetime import datetime, timezone
from marshmallow import ValidationError
from sqlalchemy import desc

comment_bp = Blueprint("comment_bp", __name__, url_prefix="/api/v1/comments")

@comment_bp.route("/add", methods=['POST'])
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
        
        parent_id = data.get("parent_id", None)
        
        if parent_id:
            parent_comment= session.query(Comment).filter(Comment.id == Comment.parent_id).first()
            if not parent_comment:
                return api_response(True, "Parent comment not found!", None, 404)
            
        new_comment = Comment(
            post_id = validate_data["post_id"],
            content = validate_data["content"],
            user_id = current_user.id,
            parent_id = parent_id
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
    """
    📝 Endpoint Documentation
    
    Endpoint:
    GET /api/v1/comments/get_by_post/<post_id>
    ---
    == Description: ==
    Fetch all comments for a specific post.This endpoint retrieves a paginated list of 
    comments associated with a given post ID. Each comment includes essential comment
    details and information about the user who posted it (such as username and email). 
    It ensures only authenticated users (with valid JWT tokens) can access the data.
    """

    session = SessionLocal()
    try:
        try:
            # Get query parameter for pagination(default: page=1, per_page=10)
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
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


@comment_bp.route("/get_by_user/<string:user_id>", methods=['GET'])
@token_required
def get_by_user(user_id):
    session = SessionLocal()
    current_user = g.current_user
    try:
        # Restrict access: user can only view their own comments. (optional)
        if current_user.id != user_id:
            return api_response(True, "Unauthorized access!", None, 403)

        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return api_response(True, "Invalid pagination parameter", None, 400)
        

        comments = session.query(Comment, Post).join(Post, Comment.post_id == Post.id).filter(Comment.user_id == user_id).order_by(desc(Comment.created_at)).offset((page - 1)* per_page).limit(per_page).all()
        
        if not comments:
            return api_response(True, "No comments found for this user!", [], 404)
        
        result = []
        for comment, post in comments:
            result.append({
                "comment_id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at,
                "post": {
                    "post_id": str(post.id),
                    "title": post.title
                }
            })

        return api_response(False, "Fetched comments by user successfully", {
            "comment_data": result,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": session.query(Comment).filter(Comment.user_id == user_id).count()
            }
        }, 200)
    
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch comments by user", str(e), 500)
    finally:
        session.close()


@comment_bp.route("/update/<string:comment_id>", methods=['PUT'])
@token_required
def update_comment(comment_id):
    """
    📝 Endpoint Documentation 
    
    Endpoint:
    PUT /api/v1/comments/update/<string:comment_id>
    ---
    == Description: ==
    This endpoint allows an authenticated user to update their own comment 
    by providing the new content in the request body.
    """
    
    session = SessionLocal()
    current_user = g.current_user
    
    try:
        '''Get request body'''
        data = request.get_json() or {}
        if not data.get("content"):
            return api_response(True, "Content is required!", None, 400)
        
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return api_response(True, "Comment not found!", [], 404)
        
        if comment.user_id != current_user.id:
            return api_response(True, "Unauthorized! You can only edit your own comments.", None, 403)

        '''Validate incomming data & Update content'''
        validate_data = CommentSchema().load(data, partial=True)   # partial=True allows updating specific fields
        comment.content = validate_data['content']
        comment.updated_at = datetime.now(timezone.utc)

        session.commit()

        return api_response(False, "Comment updated successfully.", CommentSchema().dump(comment), 200)
            
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to update comment.", str(e), 500)
    finally:
        session.close()



@comment_bp.route("/delete/<string:comment_id>", methods=['DELETE'])
@token_required
def delete_comment(comment_id):
    session = SessionLocal()
    current_user = g.current_user
    
    try:
      comment = session.query(Comment).filter(Comment.id == comment_id).first()
      if not comment:
          return api_response(True, "Commnet not found!", None, 404)
      if comment.user_id != current_user.id:
          return api_response(True, "Unauthorized! You can only delete your own comments.", None, 403)
      
      session.delete(comment)
      session.commit()
      
      return api_response(False, "Comment deleted successfully!", None, 200)
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to delete comment", str(e), 500)
    finally:
        session.close()
    