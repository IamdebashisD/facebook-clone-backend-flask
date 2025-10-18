from marshmallow import Schema, fields, validate

class PostSchema(Schema):
    '''
    Schema for validating and serializing Post data.
    '''
    id = fields.Str(dump_only=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={
            "required": "Title is required"
        }
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            "required": "Content is required.",
            "null": "Content cannot be null.", 
        }
    )
    user_id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)