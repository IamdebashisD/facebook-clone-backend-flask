from marshmallow import Schema, fields, validate

class CommentSchema(Schema):
    
    id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    post_id = fields.Str(required=True)
    user_id = fields.Str(dump_only=True)
    
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            "required": "Content is required",
        }
    )