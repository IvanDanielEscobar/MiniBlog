from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

def role_required(*roles):
    #lista de roles permitidos, ej: 'admin', 'moderator'
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity or identity.get("role") not in roles:
                return jsonify({"error": "Permiso denegado"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
