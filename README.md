# MiniBlog EFI - Python 1

API REST del MiniBlog desarrollada con **Flask**, **JWT** y control de roles (**user**, **moderator**, **admin**) que permite gestionar usuarios, posts, comentarios y categorías de manera segura y organizada.

Para empezar, primero clona el repositorio usando HTTPS: `git clone https://github.com/IvanDanielEscobar/MiniBlog.git` o SSH: `git@github.com:IvanDanielEscobar/MiniBlog.git`

Entra en la carpeta del proyecto con `cd MiniBlog`.

Instala **Astral UV**
`sudo snap install astral-uv --classic` e inicialízalo con `uv init`.

Agrega todas las dependencias necesarias: `blinker`, `click`, `Flask`, `Flask-SQLAlchemy`, `greenlet`, `itsdangerous`, `Jinja2`, `MarkupSafe`, `marshmallow`, `marshmallow-sqlalchemy`, `PyMySQL`, `SQLAlchemy`, `typing_extensions`, `Werkzeug`, `bcrypt<4.0`, `Flask-JWT-Extended`, `passlib[bcrypt]==1.7.4` y `flask-cors>=6.0.1`.

Luego sincroniza UV con `uv sync` e inicia el proyecto con `uv run flask run --reload`.

🔥 El servidor quedará corriendo en `http://127.0.0.1:5000`.

## Dependecias necesarias:

"blinker",
"click",
"Flask",
"Flask-SQLAlchemy",
"greenlet",
"itsdangerous",
"Jinja2",
"MarkupSafe",
"marshmallow",
"marshmallow-sqlalchemy",
"PyMySQL",
"SQLAlchemy",
"typing_extensions",
"Werkzeug",
"bcrypt<4.0",
"Flask-JWT-Extended",
"passlib[bcrypt]==1.7.4",
"flask-cors>=6.0.1",

## Autenticación

    roles: user, admin

## Registrar usuario

    POST /register
    Body: { "name": "nombre", "email": "nombre@correo.com", "password": "1234", "role": "role"}

## Login

    POST /login
    Body: { "email": "ivan@correo.com", "password": "1234" }
    Response: { "access_token": "<JWT>" }

## Posts

# Listar posts (público)

    GET /posts

# Crear post (usuario autenticado)

    POST /posts
    Headers: Authorization: Bearer <JWT>
    Body: { "title": "Mi primer post", "content": "Contenido..." }

# Editar post (solo autor o admin)

    PUT /posts/<id>

# Eliminar post (solo autor o admin)

    DELETE /posts/<id>

## Comentarios

# Listar comentarios de un post

    GET /posts/<post_id>/comments

# Crear comentario (usuario autenticado)

    POST /posts/<post_id>/comments
    Body: { "user_id": 3, "content": "Comentario..." }

# Eliminar comentario (autor, admin)

    DELETE /comments/<id>

## Categorías

# Listar categorías (público)

    GET /categories

# Crear categoría (admin)

    POST /categories
    Body: { "name": "Deportes" }

# Editar categoría (admin)

    PUT /categories/<id>

# Eliminar categoría (solo admin)

    DELETE /categories/<id>

## Usuarios

# Listar todos los usuarios(público)

    GET /users

# Cambiar rol de usuario(solo admin)

    PATCH /users/<id>/role
    Body: { "role": "moderator" }

# Desactivar usuario(solo admin)

    DELETE /users/<id>

👥 Integrantes del Proyecto

Iván Escobar.
Jonatan Villavicencio.
