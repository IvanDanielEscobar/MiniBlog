from app import db

from marshmallow import Schema, fields

from models import User, Review

class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    movie_id = fields.Int()
    rating = fields.Int()
    comment = fields.Str(allow_none=True)
    date = fields.Date(allow_none=True)
    user = fields.Nested("UserSchema", only=["name"], dump_only=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    reviews = fields.List(
        fields.Nested(
            "ReviewSchema", 
            exclude=("user", "user_id")
        ),
        dump_only=True
    )

class RegisterSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(load_only=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    