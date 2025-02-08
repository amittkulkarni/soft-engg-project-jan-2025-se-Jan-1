from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import jsonify

def generate_token(user_id):
    return create_access_token(identity=user_id)

def get_current_user():
    return get_jwt_identity()

def protected_route():
    @jwt_required()
    def wrapper(func):
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return decorator
    return wrapper
