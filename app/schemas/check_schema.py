import datetime
from user_schema import UserSchema, ValidationError

new_user = {
    "username":"debashisdas", 
    "email": "das.debashis626@gmail.com",
    "password":"dggydct"
}

schema = UserSchema()
try:
    # Use the load() method to trigger validation
    loaded_data = schema.load(new_user)
    print("Validation Successful:", loaded_data)
except ValidationError as err:
    print("Validation Error Occurred:")
    print(err.messages)