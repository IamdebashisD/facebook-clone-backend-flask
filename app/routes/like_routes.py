from flask import Blueprint, g
from app.database.db import SessionLocal
from app.models.like_model import Like
from app.models.post_model import Post
from app.models.user_model import User
from app.utils.token_required import token_required
from app.utils.response_helper import api_response
from sqlalchemy.exc import IntegrityError


like_bp = Blueprint("like_bp", __name__, url_prefix="/api/v1/like")

@like_bp.route("/toggle_like/<string:post_id>", methods=['POST'])
@token_required
def toggle_like(post_id):
    session = SessionLocal()
    current_user = g.current_user

    try:
        post = session.query(Post).filter(Post.id == post_id).first()
        if not post:
            return api_response(True, "Post not found!", None, 404)
        
        like = session.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.id).first()
        
        if like:
            session.delete(like)
            session.commit()
            return api_response(False, "Liked removed", {"liked": False}, 200)
        else:
            new_like = Like(post_id=post_id, user_id=current_user.id)
            session.add(new_like)
            session.commit()
            return api_response(False, "Post liked", {"liked": True}, 201)
        
    except IntegrityError:
        session.rollback()
        return api_response(False, "Already liked", {"liked": True}, 200)
    
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to toggle like!", str(e), 500)
    finally:
        session.close()


@like_bp.route("/count/<string:post_id>", methods=['GET'])
@token_required
def get_like_count(post_id):
    session = SessionLocal()

    try:
        # Check if post exists
        post = session.query(Post).filter(Post.id == post_id).first()
        if not post:
            return api_response(True, "Post not found!", None, 404)

        # Count likes for the post
        like_count = session.query(Like).filter(Like.post_id == post_id).count()

        return api_response(
            False,
            "Total likes fetched successfully.",
            {
                "post_id": post_id, 
                "total_likes": like_count
            },
            200
        )

    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch like count.", str(e), 500)

    finally:
        session.close()


@like_bp.route("/is_liked/<string:post_id>", methods=["GET"])
@token_required
def is_liked(post_id):
    """
    Endpoint:
    GET /likes/is-liked/<post_id>

    Description:
    Returns whether the current user has already liked the post.

    -- json --
    {
        "error_code": false,
        "message": "Like status fetched",
        "data": { "liked": true }
    }
    """
    session = SessionLocal()
    current_user = g.current_user    
    try:
        post_exists = session.query(Post).filter(Post.id == post_id).first()
        if not post_exists:
            return api_response(True, "Post not found!", None, 404)
        
        is_liked = session.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.id).first()
        liked = is_liked is not None       # Convert to boolean
        return api_response(False, "Like status fetched successfully", {"is_liked": liked}, 200)
        
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch like status", str(e), 500)
    finally:
        session.close()   
        

@like_bp.route("/list_of_users_liked_to_a_post/<string:post_id>", methods=['GET'])
@token_required
def get_post_likes_With_users(post_id):
    session = SessionLocal()
    try:
        # check if a post exist
        post = session.query(Post).filter(Post.id == post_id).first()
        if not post:
            return api_response(True, "Post not found!", None, 404)
        
        likes = session.query(Like, User).join(User, Like.user_id == User.id).filter(Like.post_id == post_id).all()
        
        total_likes = len(likes)
        
        users = []
        for like, user in likes:
            users.append({
                "user_id": user.id,
                "username": user.username
            })
        
        return api_response(False, "Post likes fetched successfully", {"total_likes": total_likes, "users": users}, 200)
        
    except Exception as e:
        session.rollback()
        return api_response(True, "Failed to fetch likes data", str(e), 500)
    finally:
        session.close() 
        
        