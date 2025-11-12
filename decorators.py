from functools import wraps
from flask_jwt_extended import get_jwt
from flask import jsonify

def role_required(*roles):
    #lista de roles permitidos, ej: 'admin', 'moderator'
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")

            if roles and user_role not in roles:
                return jsonify({"error": "Permiso denegado"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
