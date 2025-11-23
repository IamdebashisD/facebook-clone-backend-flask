from marshmallow import Schema, fields, validate


class userMiniSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    
    
    
class replySchema(Schema):
    id = fields.Str(dump_only=True)
    post_id = fields.Str(required=True)
    user_id = fields.Str(dump_only=True)
    user = fields.Nested(userMiniSchema)
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            "required": "Content is required",
        }
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    
    
class CommentSchema(Schema):
    class Meta:
        ordered = True
    
    id = fields.Str(dump_only=True)
    post_id = fields.Str(required=True)
    user_id = fields.Str(dump_only=True)
    user = fields.Nested(userMiniSchema)
    
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            "required": "Content is required",
        }
    )
    # List of replies
    replies = fields.List(fields.Nested(replySchema), dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)