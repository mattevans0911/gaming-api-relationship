from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Games(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    rating = db.Column(db.String, nullable = False)
    console_used = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    games_fk = db.Column(db.Integer, db.ForeignKey('console.id'))

    def __init__(self, name, rating, console_used, price, games_fk):
        self.name = name
        self.rating = rating
        self.console_used = console_used
        self.price = price
        self.games_fk = games_fk

class GameSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'rating', 'console_used', 'price', 'games_fk')
    
game_schema = GameSchema()
multiple_game_schema = GameSchema(many=True)


class Console(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    manufacturer = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    games = db.relationship('Games', backref = 'console', cascade = 'all, delete, delete-orphan')


    def __init__(self, manufacturer, name, price):
        self.manufacturer = manufacturer
        self.name = name
        self.price = price


class ConsoleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'manufacturer', 'name', 'price', 'games')
    games = ma.Nested(multiple_game_schema)
    

console_schema = ConsoleSchema()
multiple_console_schema = ConsoleSchema(many=True)



#Games End Points
@app.route('/game/add', methods = ["POST"])
def add_game():
    post_data = request.get_json()
    name = post_data.get('name')
    rating = post_data.get('rating')
    console_used = post_data.get('console_used')
    price = post_data.get('price')
    games_fk = post_data.get('games_fk')

    new_game = Games(name, rating, console_used, price, games_fk)
    db.session.add(new_game)
    db.session.commit()

    return jsonify('Game added successfully')

@app.route('/game/get', methods = ["GET"])
def get_games():
    games = db.session.query(Games).all()
    return jsonify(multiple_game_schema.dump(games))

@app.route('/game/get/<id>', methods = ["GET"])
def get_game(id):
    game = db.session.query(Games).filter(Games.id == id).first()
    return jsonify(game_schema.dump(game))


#Console End Points
@app.route('/console/add', methods = ["POST"])
def add_console():
    post_data = request.get_json()
    manufacturer = post_data.get('manufacturer')
    name = post_data.get('name')
    price = post_data.get('price')


    new_console = Console(manufacturer, name, price)
    db.session.add(new_console)
    db.session.commit()

    return jsonify("Console added successfully")

@app.route('/console/get', methods = ["GET"])
def get_console():
    consoles = db.session.query(Console).all()
    return jsonify(multiple_console_schema.dump(consoles))

@app.route('/console/get/<id>')
def get_one_console(id):
    console = db.session.query(Console).filter(Console.id == id).first()
    return jsonify(console_schema.dump(console))


if __name__ == "__main__":
    app.run(debug=True)