from marshmallow import Schema, fields


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
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
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
    
class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_published = fields.Bool(dump_only=True)
    author = fields.Nested(lambda: UserSchema(only=("id", "name", "email")))
    comments = fields.List(fields.Nested(lambda: CommentSchema(only=("id","content","author","created_at"))))
    genres = fields.List(fields.Nested(lambda: GenreSchema(only=("id", "name"))))
    categories = fields.List(fields.Nested(lambda: CategorySchema(only=("id", "name"))))


class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    is_visible = fields.Bool(dump_only=True)
    author = fields.Nested(lambda: UserSchema(only=('id', 'name')))
    post = fields.Nested(lambda: PostSchema(only=('id', 'title')))

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    year = fields.Int(required=True)
    genres = fields.List(fields.Nested(lambda: GenreSchema(only=('id', 'name'))))
    reviews = fields.List(fields.Nested(lambda: ReviewSchema(exclude=('movie',))))

class UserCredentialsSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    role = fields.Str()