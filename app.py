import requests

from flask import Flask, flash, render_template, request, redirect, url_for
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

app = Flask(__name__)


app.secret_key = "cualquiercosa"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@localhost/flask_app"
)

# db extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_contact')
def add_contact():
    return 'add contact'


@app.route('/edit')
def edit_contact():
    return 'edit contact'


@app.route('/delete_contact')
def delete_contact():
    return 'delete contact'

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


if __name__ == '__main__':
    app.run(debug=True)