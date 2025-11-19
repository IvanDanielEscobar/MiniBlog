from flask import request, Flask, jsonify
from marshmallow import ValidationError
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token,
    create_refresh_token
)
from passlib.hash import bcrypt
from decorators import role_required

from services.user_service import UserService, AuthService
from services.post_service import PostService
from services.comment_service import CommentService
from services.category_service import CategoryService

from models import User, UserCredentials, Post, db, Comment, Category
from schemas import UserSchema, RegisterSchema, LoginSchema, CommentSchema, PostSchema, CategorySchema


user_service = UserService()
post_service = PostService()
comment_service = CommentService()
category_service = CategoryService()

# ------- USERS
class UserAPI(MethodView):
    @jwt_required()
    @role_required()
    def get(self):
        users = User.query.all()
        return UserSchema(many=True).dump(users)

    @role_required("admin")
    def post(self):
        try:
            data = UserSchema().load(request.json)
            new_user = user_service.create_user(data)
            return UserSchema().dump(new_user), 201
        
        except ValidationError as err:
            return {"Errors": f"{err.messages}"}, 400
        
        except ValueError as err:
            return {"Errors": str(err)}, 400


class UserDetailAPI(MethodView):
    @jwt_required()
    def get(self, id):
        try:
            user = user_service.get_user(id)
            return UserSchema().dump(user), 200
        except ValueError as err:
            return {"error": str(err)}, 404

    
    @jwt_required()
    def put(self, id):
        try: 
            data = UserSchema().load(request.json)
            updated_user = user_service.update_user(id, data)
            return UserSchema().dump(updated_user), 200
        except ValidationError as err:
            return {"Error": err.messages}, 400
        except ValueError as err:
            return {"error": str(err)}, 400
        

    @jwt_required()
    def patch(self, id):
        try: 
            data = UserSchema(partial=True).load(request.json)
            updated_user = user_service.update_user(id, data)
            return UserSchema().dump(updated_user), 200
        except ValidationError as err:
            return {"Error": err.messages}, 400
        except ValueError as err:
            return {"error": str(err)}, 400
        
    @jwt_required()
    @role_required("admin")
    def delete(self, id):
        try:
            user_service.delete_user(id)
            return {"Message": "Deleted User"}, 204
        except ValueError as err:
            return {"error": str(err)}, 404
        except Exception:
            return {"Error": "No es posible borrarlo"}, 400


class UserRegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.json)
        except ValidationError as err:
            return {"Error": err.messages}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {"Error": "Email en uso"}, 400
        
        role = data.get('role', 'user')

        new_user = User(
            name=data["name"],
            email=data['email']
            )
        db.session.add(new_user)
        db.session.flush()

        password_hash = bcrypt.hash(data['password'])

        credenciales = UserCredentials(
            user_id=new_user.id,
            password_hash=password_hash,
            role=role
        )
        db.session.add(credenciales)
        db.session.commit()
        return UserSchema().dump(new_user), 201


# --------- AUTH LOGIN
class AuthLoginAPI(MethodView):
    def post(self):
        try:
            data = LoginSchema().load(request.json)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        try:
            service = AuthService()
            result = service.login(
                email=data["email"],
                password=data["password"]
            )
            return result, 200

        except ValueError as err:
            return {"errors": {"credentials": [str(err)]}}, 401
        
#------------- POSTS
class PostAPI(MethodView):
    @jwt_required()
    @role_required()
    def get(self):
        result = post_service.list_posts()
        return jsonify(result), 200
                    

    @jwt_required()
    @role_required()
    def post(self):
        data = request.json
        if not data.get("title") or not data.get("content"):
            return {"error": "title y content son obligatorios"}, 400
        
        user_id = int(get_jwt_identity())

        result = post_service.create_post(data, user_id)
        return result, 201

class PostDetailAPI(MethodView):
    @jwt_required()
    def delete(self, id):
        post = post_service.repo.get_by_id(id)

        user_id = int(get_jwt_identity())
        role = get_jwt()["role"]

        if role != "admin" and post.user_id != user_id:
            return {"error": "No autorizado para modificar este post"}, 403

        post_service.delete_post(post)
        return {"message": "Post eliminado"}, 200

    @jwt_required()
    def put(self, id):
        post = post_service.repo.get_by_id(id)
        user_id = int(get_jwt_identity())
        role = get_jwt()["role"]

        if role != "admin" and post.user_id != user_id:
            return {"error": "No autorizado para modificar este post"}, 403

        data = request.json
        post_service.update_post(post, data)
        return {"message": "Post actualizado"}, 200
    
class CommentAPI(MethodView):

    @jwt_required(optional=True)
    @role_required()
    def get(self, post_id):
        result = comment_service.list_comments(post_id)
        return jsonify(result)
    
    @jwt_required()
    @role_required()
    def post(self, post_id):
        data = request.json
        content = data.get("content")

        if not content:
            return {"error": "Falta Contenido"}, 400

        user_id = int(get_jwt_identity())
        
        result = comment_service.create_comment(post_id, user_id, content)

        return jsonify(result), 201


class CommentDetailAPI(MethodView):
    @jwt_required()
    def delete(self, comment_id):
        claims = get_jwt()
        user_id = int(get_jwt_identity())

        comment = comment_service.repo.get_comment_or_404(comment_id)

        # Solo autor, moderador o admin puede borrar
        if user_id != comment.user_id and claims["role"] not in ["moderator", "admin"]:
            return {"error": "No autorizado"}, 403

        # eliminacion logica
        comment_service.delete_comment(comment_id)
        return {"message": "Comentario eliminado"}, 200
    
    @jwt_required()
    @role_required()
    def put(self, comment_id):
        comment = comment_service.repo.get_comment_or_404(comment_id)
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        # solo el autor puede editar
        if comment.user_id != user_id:
            return {"error": "No autorizado"}, 403

        data = request.get_json()
        content = data.get("content", "").strip()
        
        if not content:
            return {"error": "Contenido vacío"}, 400

        updated = comment_service.update_comment(comment_id, content)

        return jsonify({
            "id": updated.id,
            "content": updated.content,
            "author": updated.author.name,
            "user_id": updated.user_id,
            "created_at": updated.created_at
        }), 200

class CategoryAPI(MethodView):
    def get(self):
        categories = category_service.list_categories()
        return CategorySchema(many=True).dump(categories)

    def post(self):
        data = request.json
        name = data.get("name")

        try: 
            new_category = category_service.create_category(name)        
        except ValueError as err:
            return {"error": str(err)}, 400
        return CategorySchema().dump(new_category)

class CategoryDetailAPI(MethodView):
    def put(self, id):
        data = request.json
        name = data.get("name")
        
        try:
            updated = category_service.update_category(id, name)
        except ValueError as err:
            return {"error", str(err)}, 400
        
        return CategorySchema().dump(updated), 200

# ------------ REFRESH TOKEN
class TokenRefreshAPI(MethodView):
    @jwt_required(refresh=True)  # solo con refresh token
    def post(self):
        claims = get_jwt()

        new_token = AuthService().refresh_token(claims)
        return {"access_token": new_token}, 200