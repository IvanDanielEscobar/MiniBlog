from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# relacion Post-Generos
post_genre = db.Table(
    'post_genre',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# relacion Movies-Generos
movie_genre = db.Table(
    'movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True) 
    role = db.Column(db.String(50), default='user')
    # un usuario tien muchos posts
    posts = db.relationship('Post', backref='author', lazy=True)
    # relacion con el comentario que escribe un user
    comments = db.relationship('Comment', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    #autor del post
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #comentarios del post
    comments = db.relationship('Comment', backref='post', lazy=True)
    genres = db.relationship("Genre", secondary=post_genre, backref="posts")
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    #usuario que comenta 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #donde comenta
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

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
    role = db.Column(db.String(50), nullable=False, default="user")
    user = db.relationship(
        "User", backref=db.backref("credential", uselist=False)
    )
