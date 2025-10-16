from marshmallow import Schema, fields, validate

class LikeSchema(Schema):
    
    id = fields.Str(dump_only=True)
    post_id= fields.Str(dump_only=True)
    user_id= fields.Str(dump_only=True)
    created_at = fields.Str(dump_only=True)