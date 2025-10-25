from flask import Blueprint, request, Response, g
from app.models.post_model import Post
from app.schemas.post_schema import PostSchema
from app.database.db import SessionLocal
from app.utils.token_required import token_required
from sqlalchemy.orm import Session, Query
from marshmallow import ValidationError
from app.utils.response_helper import api_response


post_bp = Blueprint("post_bp", __name__, url_prefix="/api/v1/post")

""" Route for upload post """

@post_bp.route("/upload", methods=["POST"])
@token_required
def upload_post() -> Response:
    
    session: Session =  SessionLocal()
    post_schema = PostSchema()
    current_user = g.current_user
    
    try:
        data: dict = request.get_json()
        
        if not data or not data.get("title") or not data.get("content"):
            return api_response(True, "Invalid JSON Format!", None, 400)
        
        validate_data = post_schema.load(data)
        
        new_post = Post(
            title = validate_data["title"],
            content = validate_data["content"],
            user_id = current_user.id
        )
        print("new_post ---->> ",new_post)
        
        session.add(new_post)
        session.flush()
        session.commit()
        return api_response(False, "Post created successfully", post_schema.dump(new_post), 201)
        
    except ValidationError as ve:
        return api_response(True, "Validation failed!", ve.messages, 400)
        
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to create post", str(e), 500)
        
    finally:
        session.close()



""" Route for update a post """

@post_bp.route("/update/<string:post_id>", methods=["PUT"])
@token_required
def update_post(post_id) -> Response:
    session: Session=SessionLocal()
    post_schema = PostSchema()
    current_user = g.current_user
    
    try:
        data: dict = request.get_json()
        if not data:
            return api_response(True, "Invalid JSON format!", None, 400)
        
        post: Query = session.query(Post).filter_by(id=post_id, user_id=current_user.id).first()
        if not post:
            return api_response(True, "Post not found or unauthorized", None, 404)
        
        # validate incomming data
        validate_data = post_schema.load(data, partial=True)   # partial=True allows updating specific fields
        
        for key, value in validate_data.items():
            setattr(post, key, value)
        
        session.commit()
        
        return api_response(False, "Post updated successfully", post_schema.dump(post), 200)
    
    except ValidationError as ve:
        return api_response(True, "Validation failed", ve.messages, 404)
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to update post", None, 500)
    
    finally:
        session.close()


""" Route for delete a post """

@post_bp.route("/delete/<string:post_id>", methods=["DELETE"])
@token_required
def delete_post(post_id) -> Response:
    session: Session = SessionLocal()
    current_user = g.current_user
    
    try:
        post: Query = session.query(Post).filter_by(id=post_id, user_id=current_user.id).first()
        if not post:
            return api_response(True, "Post not found or unauthorized", None, 404)

        session.delete(post)
        session.commit()    
        return api_response(False, "Post deleted successfully", None, 200)

    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to delete post", str(e), 500)
    
    finally:
        session.close()