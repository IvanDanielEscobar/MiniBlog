from flask import Flask, request
from flask_jwt_extended import JWTManager
from datetime import timedelta


from schemas import ReviewSchema

from models import db, User, Post, Comment, Movie, Review, Genre

from views import UserAPI, UserDetailAPI, UserRegisterAPI, AuthLoginAPI, PostAPI, PostDetailAPI


from flask_cors import CORS


#inicia app flask
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://BD2021:BD2021itec@143.198.156.171:3306/movies_pp1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'QueLeVayaBienProfe!UnGusto!'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

jwt = JWTManager(app)
db.init_app(app)

CORS(app, origins=["http://localhost:5173"])


app.add_url_rule(
    '/users',
    view_func=UserAPI.as_view('users_api'),
    methods=['POST', 'GET']
)
app.add_url_rule(
    '/users/<int:id>',
    view_func=UserDetailAPI.as_view('user_detail_api'),
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
)
app.add_url_rule(
    '/register',
    view_func=UserRegisterAPI.as_view('user_register_api'),
    methods=['POST']
)
app.add_url_rule(
    '/login',
    view_func=AuthLoginAPI.as_view('auth_login_api'),
    methods=['POST']
)
app.add_url_rule(
    '/posts',
    view_func=PostAPI.as_view('posts_api'),
    methods=['GET','POST']
    )
app.add_url_rule(
    '/posts/<int:id>',
    view_func=PostDetailAPI.as_view('post_detail_api'),
    methods=['PUT','DELETE']
    )

@app.route('/reviews')
def reviews():
    reviews = Review.query.all()
    return ReviewSchema(many=True).dump(reviews)

@app.route('/reviews/<int:id>', methods=['GET'])
def review(id):
    review = Review.query.get_or_404(id)
    return ReviewSchema().dump(review)

@app.route('/movies')
def movies():
    movies = Movie.query.all()
    return [
        {
            "title": movie.title,
            "year": movie.year,
            "genres": [genre.name for genre in movie.genres]
        } for movie in movies
    ]

if __name__ == '__main__':
    app.run(debug=True)