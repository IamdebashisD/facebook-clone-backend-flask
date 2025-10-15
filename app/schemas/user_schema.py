from marshmallow import Schema, fields, validate, validates, ValidationError

class UserSchema(Schema):
    
    id = fields.Str(dump_only=True)
    
    username = fields.Str( 
        required=True, 
        validate=validate.Length(min=3, max=50),
        error_messages={
            "required": "Username is required",
            "null": "Username cannot be null"
        }
    )
    email = fields.Email( 
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Please enter a valid email address."
        }
    )
    password = fields.Str(
        load_only=True,
        required=True, 
        validate=validate.Length(min=6),
        error_messages={
            "required": "Password is required.",
            "null": "Password cannot be null.",
            "invalid": "Password must be at least 6 characters long."
        }
    )
    created_at = fields.DateTime(dump_only=True)
    
    
    
    
    
'''optional validation logic'''
@validates("username")
def validation_check(self, value):
    if " " in value:
        raise ValidationError("User cannot contain spaces.")
    if not value.isalnum():
        raise ValidationError("Username should contain only letters and numbers.")