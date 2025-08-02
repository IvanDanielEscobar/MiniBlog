import requests

from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
    )

#inicia app flask
app = Flask(__name__)

#clave para sesion y config de mysql
app.secret_key = "cualquiercosa"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@localhost/flask_app"
)

# db extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from models import User, Post, Category, Comment

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #redirecciona a login si no esta autenticado


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all() #ordena los post del mas nuevo al mas viejo en orden descendente
    return render_template('index.html', posts=posts)

@app.route('/profiles')
@login_required
def profiles():
    users = User.query.all()
    return render_template('profiles.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # Pass que llega desde el formulario

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(pwhash=user.password_hash, password=password):
            login_user(user)
            session['welcome_message'] = True
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template(
        'auth/login.html'
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username exist', 'error')
            return redirect(url_for('register'))
        
        # Hasheo de contraseña
        password_hash = generate_password_hash(
            password=password,
            method='pbkdf2'
        )
        # Creacion del nuevo usuario
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Username created succefully', 'success')
        return redirect(url_for('login'))


    return render_template(
        'auth/register.html'
    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/new', methods=['GET','POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Posteado!!", "success")
        return redirect(url_for('index'))
    return render_template('new_post.html')


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id) #busca un registro id en la bd y retorna 404 si no existe
    return render_template('post_detail.html', post=post)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment_on_post(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    
    if content.strip():  # no anda si no hay nada
        comment = Comment(content=content, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
    
    return redirect(url_for('post_detail', post_id=post.id))


if __name__ == '__main__':
    app.run(debug=True)