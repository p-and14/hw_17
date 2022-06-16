# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


@movie_ns.route("/")
class MoviesView(Resource):

    def get(self):
        genre_id = request.args.get("genre_id")
        director_id = request.args.get("director_id")

        if director_id and genre_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id)
        elif director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == director_id)
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == genre_id)
        else:
            movies = Movie.query.all()

        movies_js = movies_schema.dump(movies)

        if not movies_js:
            return "Такой фильм не найден", 404

        return movies_js, 200


@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid: int):
        movie = Movie.query.get(mid)

        if not movie:
            return "Такой фильм не найден", 404

        return movie_schema.dump(movie), 200


@director_ns.route("/")
class DirectorsView(Resource):

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@director_ns.route("/<int:did>")
class DirectorView(Resource):

    def put(self, did: int):
        director = Director.query.get(did)

        if not director:
            return "Режиссёр не найден", 404

        req_json = request.json
        director.name = req_json.get("name")

        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, did: int):
        director = Director.query.get(did)

        if not director:
            return "Режиссёр не найден", 404

        db.session.delete(director)
        db.session.commit()

        return "", 204


@genre_ns.route("/")
class GenresView(Resource):

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


@genre_ns.route("/<int:gid>")
class GenreView(Resource):

    def put(self, gid: int):
        genre = Genre.query.get(gid)

        if not genre:
            return "Жанр не найден", 404

        req_json = request.json
        genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()

        return "", 204

    def delete(self, gid: int):
        genre = Genre.query.get(gid)

        if not genre:
            return "Жанр не найден", 404

        db.session.delete(genre)
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
