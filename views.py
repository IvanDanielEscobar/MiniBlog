from flask import request
from marshmallow import ValidationError
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)
from passlib.hash import bcrypt
from utils.decorators import role_required

from app import db
from models import User, UserCredentials, Post
from schemas import UserSchema, RegisterSchema, LoginSchema


class UserAPI(MethodView):
    @jwt_required()
    def get(self):
        users = User.query.all()
        return UserSchema(many=True).dump(users)

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
    def get(self, id):
        user = User.query.get_or_404(id)
        return UserSchema().dump(user), 200
    
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
            return {"Error": err}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {"Error": "Email en uso"}, 400
        
        new_user = User(name=data["name"], email=data['email'])
        db.session.add(new_user)
        db.session.flush()
        password_hash = bcrypt.hash(data['password'])
        role = data.get('role', 'user')

        credenciales = UserCredentials(
            user_id=new_user.id,
            password_hash=password_hash,
            role=role
        )
        db.session.add(credenciales)
        db.session.commit()
        return UserSchema().dump(new_user), 201


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
        identity = {
            "id": user.id,
            "email": user.email,
            "role": user.credential.role,
        }
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
            }, 200


class PostAPI(MethodView):
    @jwt_required()
    def get(self):
        posts = Post.query.all()
        return [{
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author": post.author.name,
            "genres": [g.name for g in post.genres]
        } for post in posts], 200

    @jwt_required()
    def post(self):
        data = request.json
        user_id = get_jwt_identity()["id"]

        new_post = Post(
            title=data.get("title"),
            content=data.get("content"),
            user_id=user_id
        )

        db.session.add(new_post)
        db.session.commit()
        return {"message": "Post creado", "id": new_post.id}, 201

class PostDetailAPI(MethodView):
    @jwt_required()
    @role_required("admin", "moderator")
    def delete(self, id):
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post eliminado"}, 200

    @jwt_required()
    @role_required("admin", "moderator")
    def put(self, id):
        post = Post.query.get_or_404(id)
        data = request.json
        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        db.session.commit()
        return {"message": "Post actualizado"}, 200
    
class TokenRefreshAPI(MethodView):
    @jwt_required(refresh=True)  # solo con refresh token
    def post(self):
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        return {"access_token": new_access_token}, 200