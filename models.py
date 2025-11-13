from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# relacion Post-Generos
post_genre = db.Table(
    'post_genre',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# relacion Movies-Generos
movie_genre = db.Table(
    'movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)
# Tabla intermedia Post-Category
post_category = db.Table(
    'post_category',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)




class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("1")
        ) 
    
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now()) 
    credential = db.relationship("UserCredentials", back_populates="user", uselist=False)
    
    # un usuario tien muchos posts
    posts = db.relationship('Post', back_populates='author', lazy=True)
    # relacion con el comentario que escribe un user
    comments = db.relationship('Comment', back_populates='author', lazy=True)

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())  # NUEVO
    is_active = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("1")
        )#igual a is_published
    #autor del post
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')
    #comentarios del post
    comments = db.relationship('Comment', back_populates='post', lazy=True)
    genres = db.relationship("Genre", secondary=post_genre, backref="posts")
    categories = db.relationship("Category", secondary="post_category", back_populates="posts")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    #usuario que comenta 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #donde comenta
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    # Eliminado logico
    is_visible = db.Column(db.Boolean, default=True, nullable=False)

    author = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    #Un post puede tener varias categorias
    posts = db.relationship("Post", secondary="post_category", back_populates="categories")



class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(200), nullable=False
    )
    year = db.Column(db.Integer, nullable=False)
    genres = db.relationship(
        "Genre",
        secondary="movie_genre",
        backref="movies",
    )
    reviews = db.relationship(
        "Review", backref="movie", lazy=True
    )


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(50), nullable=False
    )


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    movie_id = db.Column(
        db.Integer,
        db.ForeignKey("movies.id"),
        nullable=False,
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date = db.Column(db.Date)


class UserCredentials(db.Model):
    __tablename__ = "user_credentials"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="user")
    
    user = db.relationship(
        "User",
        back_populates="credential"
        )
    
