from flask import Blueprint, request, Response, g
from app.models.post_model import Post
from app.schemas.post_schema import PostSchema
from app.database.db import SessionLocal
from app.utils.token_required import token_required
from sqlalchemy.orm import Session, Query
from sqlalchemy import or_, desc
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
        

@post_bp.route("/get_all_posts", methods=['GET'])
@token_required
def get_all_post():
    """
    Get all posts with optional search, sorting, and pagination.

    ---
    == Description: ==
    This endpoint retrieves a list of posts from the database.
    It supports search filtering by title or content, sorts posts by creation date
    (newest first), and allows pagination through query parameters.

    == Query Parameters: ==
    - `page` (int, optional): Page number to retrieve (default: 1)
    - `per_page` (int, optional): Number of posts per page (default: 10)
    - `search` (string, optional): Keyword to filter posts by title or content

    == Headers: ==
    - `Authorization`: Bearer token required for authentication

    == Responses: ==
    - `200 OK`: Returns list of posts with pagination info
    - `404 Not Found`: No posts found for the given filters
    - `400 Bad Request`: Invalid pagination parameters
    - `500 Internal Server Error`: Unexpected server error
    """
    session = SessionLocal()
    try:
        try:     
            # Get query parameters (default: page=1, per_page=10)
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return api_response(True, "Invalid paginatin parameter", [], 400)
        # Get query param for search (default: search=None)
        search = request.args.get("search", None)
        
        # Build Base query
        query = session.query(Post)
        
        if search:
            query = query.filter(
                or_(Post.title.ilike(f'%{search}%'), Post.content.ilike(f'%{search}%'))
            )
        # Apply sorting (latest first)
        query = query.order_by(desc(Post.created_at))
        
        # Count total records before pagination
        total = query.count()
        
        # Apply pagination here
        posts = query.offset((page -1) * per_page).limit(per_page).all()
        if not posts:
            return api_response(False, "No posts found", [], 404)
        
        # Serialize post via marshmallow schema
        post_schema = PostSchema(many=True)
        post_data = post_schema.dump(posts)
        
        return api_response(
            False,
            "Fetch all post successfully.",
            {
                "post_data": post_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total
                },
            },
            200
        )
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch posts!", str(e), 500)
    finally:
        session.close()