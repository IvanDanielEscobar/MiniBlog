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

from models import User, UserCredentials, Post, db, Comment, Category
from schemas import UserSchema, RegisterSchema, LoginSchema, CommentSchema, PostSchema, CategorySchema

user_service = UserService()
post_service = PostService()

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
        # listar comentarios visibles de un post
        post = Post.query.get_or_404(post_id)
        return jsonify([
            {
                "id": c.id,
                "content": c.content,
                "author": c.author.name,
                "user_id": c.user_id,  
                "created_at": c.created_at
            } for c in post.comments if c.is_visible
        ])
    
    
    
    @jwt_required()
    @role_required()
    def post(self, post_id):
        data = request.json
        user_id = data.get("user_id")
        content = data.get("content")

        if not content:
            return {"error": "Falta Contenido"}, 400
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        post = Post.query.get(post_id)
        if not user or not post:
            return jsonify({"error": "Usuario o post no encontrado"}), 404
        
        comment = Comment(content=content, user_id=user_id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            "id": comment.id,
            "content": comment.content,
            "author": comment.author.name,
            "post_id": comment.post_id,
            "created_at": comment.created_at
        }), 201


class CommentDetailAPI(MethodView):
    @jwt_required()
    def delete(self, comment_id):
        comment = Comment.query.get_or_404(comment_id)
        claims = get_jwt()
        user_id = int(get_jwt_identity())

        # Solo autor, moderador o admin puede borrar
        if user_id != comment.user_id and claims["role"] not in ["moderator", "admin"]:
            return {"error": "No autorizado"}, 403

        # eliminacion logica
        comment.is_visible = False
        db.session.commit()
        return {"message": "Comentario eliminado"}, 200
    @jwt_required()
    @role_required()
    def put(self, comment_id):
        comment = Comment.query.get_or_404(comment_id)
        user_id = int(get_jwt_identity())
        claims = get_jwt()

        # solo el autor puede editar
        if comment.user_id != user_id:
            return {"error": "No autorizado"}, 403

        data = request.get_json()
        content = data.get("content", "").strip()
        if not content:
            return {"error": "Contenido vacío"}, 400

        comment.content = content
        db.session.commit()

        return jsonify({
            "id": comment.id,
            "content": comment.content,
            "author": comment.author.name,
            "user_id": comment.user_id,
            "created_at": comment.created_at
        }), 200

class CategoryAPI(MethodView):
    def get(self):
        categories = Category.query.all()
        return CategorySchema(many=True).dump(categories)

    def post(self):
        data = request.json
        name = data.get("name")
        if not name: 
            return {"error": "Nombre olbigarotio"}, 400
        
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return CategorySchema().dump(category)

class CategoryDetailAPI(MethodView):
    def put(self, id):
        category = Category.query.get_or_404(id)
        data = request.json
        category.name = data.get("name", category.name)
        db.session.commit()
        return CategorySchema().dump(category), 200
    def delete(self, id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return {"message": "Categoría eliminada"}, 200


# ------------ REFRESH TOKEN
class TokenRefreshAPI(MethodView):
    @jwt_required(refresh=True)  # solo con refresh token
    def post(self):
        identity = get_jwt_identity()
        claims = get_jwt()
        new_access_token = create_access_token(identity=identity, additional_claims=claims)
        return {"access_token": new_access_token}, 200