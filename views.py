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

from models import User, UserCredentials, Post, db, Comment
from schemas import UserSchema, RegisterSchema, LoginSchema, CommentSchema, PostSchema


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
            new_user = User(
                name=data.get('name'),
                email=data.get('email')
            )
            db.session.add(new_user)
            db.session.commit()
        except ValidationError as err:
            return {"Errors": f"{err.messages}"}, 400
        return UserSchema().dump(new_user), 201


class UserDetailAPI(MethodView):
    @jwt_required()
    def get(self, id):
        user = User.query.get_or_404(id)
        return UserSchema().dump(user), 200
    
    @jwt_required()
    def put(self, id):
        user = User.query.get_or_404(id)
        try: 
            data = UserSchema().load(request.json)
            user.name = data['name']
            user.email = data['email']
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return {"Error": err.messages}
        
    @jwt_required()
    def patch(self, id):
        user = User.query.get_or_404(id)
        try: 
            data = UserSchema(partial=True).load(request.json)
            if 'name' in data:
                user.name = data.get('name')
            if 'email' in data:
                user.email = data.get('email')
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return {"Error": err.messages}, 400
        
    @jwt_required()
    @role_required("admin")
    def delete(self, id):
        user = User.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {"Message": "Deleted User"}, 204
        except:
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
        
        user = User.query.filter_by(email=data["email"]).first()

        if not user or not user.credential:
            return {"errors": {"credentials": ["Inválidas"]}}, 401
        
        if not bcrypt.verify(data["password"], user.credential.password_hash):
            return {"errors": {"credentials": ["Inválidas"]}}, 401
        
        identity = str(user.id)
        additional_claims = {
            "email": user.email,
            "role": user.credential.role
        }

        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
            )
        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims=additional_claims
            )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
            }, 200


#------------- POSTS
class PostAPI(MethodView):
    @jwt_required()
    @role_required()
    def get(self):
        posts = Post.query.filter_by(is_active=True).all()
        result = []
        for post in posts:
            result.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author.name,
                "genres": [g.name for g in post.genres],
                "comments": [
                    {
                        "id": c.id,
                        "content": c.content,
                        "author": c.author.name,
                        "created_at": c.created_at
                    } for c in post.comments if c.is_visible
                ]
            })
        return jsonify(result)
                    

    @jwt_required()
    @role_required()
    def post(self):
        data = request.json
        if not data.get("title") or not data.get("content"):
            return {"error": "title y content son obligatorios"}, 400
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        role = claims["role"]

        new_post = Post(
            title=data.get("title"),
            content=data.get("content"),
            user_id=user_id
        )
        try:
            db.session.add(new_post)
            db.session.commit()
        except: 
            db.session.rollback()
        return {"message": "Post creado", "id": new_post.id}, 201

class PostDetailAPI(MethodView):
    @jwt_required()
    def delete(self, id):
        post = Post.query.get_or_404(id)
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        role = claims["role"]

        if role != "admin" and post.user_id != user_id:
            return {"error": "No autorizado para modificar este post"}, 403

        post.is_active = False #eliminado logico
        db.session.commit()
        return {"message": "Post eliminado"}, 200

    @jwt_required()
    def put(self, id):
        post = Post.query.get_or_404(id)
        identity = get_jwt_identity()
        claims = get_jwt()
        user_id = int(identity)
        role = claims["role"]

        if role != "admin" and post.user_id != user_id:
            return {"error": "No autorizado para modificar este post"}, 403

        data = request.json
        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        db.session.commit()
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
                "created_at": c.created_at
            } for c in post.comments if c.is_visible
        ])

    @jwt_required()
    @role_required()
    def post(self, post_id):
        data = request.json
        user_id = data.get("user_id")
        content = data.get("content")

        if not all ([user_id, content]):
            return {"error": "Faltan Datos"}, 400
        
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
        db.session.add(categories)
        db.session.commit()
        return CategorySchema().dump(categories)

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