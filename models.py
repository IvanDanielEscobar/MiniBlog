from app import db

from flask_login import UserMixin


# relacion Post-Category
post_category = db.Table(
    'post_category',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True) 
    
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #comentarios del post
    comments = db.relationship('Comment', backref='post', lazy=True)
    categories = db.relationship('Category', secondary=post_category, back_populates='posts')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    #usuario que comenta 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #donde comenta
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    posts = db.relationship('Post', secondary=post_category, back_populates='categories')