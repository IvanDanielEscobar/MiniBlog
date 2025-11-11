from flask import Flask, request
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token,
    create_refresh_token
)
from datetime import timedelta


from schemas import ReviewSchema

from models import db, Movie, Review

from views import UserAPI, UserDetailAPI, UserRegisterAPI, AuthLoginAPI, PostAPI, PostDetailAPI


from flask_cors import CORS


#inicia app flask
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://BD2021:BD2021itec@143.198.156.171:3306/movies_pp1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '1234'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()


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

@app.route("/debug-token")
@jwt_required()
def debug_token():
    return {
        "identity": get_jwt_identity(),
        "claims": get_jwt()
    }


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