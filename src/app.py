"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People,Planet,Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# USERS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


# PEOPLE
@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    return jsonify([p.serialize() for p in people_list]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_people(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/people', methods=['POST'])
def create_people():
    data = request.get_json()
    name = data.get("name")
    gender = data.get("gender")
    if not name:
        return jsonify({"msg": "Name is required"}), 400
    new_person = People(name=name, gender=gender)
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


# PLANETS
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    name = data.get("name")
    population = data.get("population")
    if not name:
        return jsonify({"msg": "Name is required"}), 400
    new_planet = Planet(name=name, population=population)
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201


# FAVORITES
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.get(1) 
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    result = []
    for fav in user.favorites:
        if fav.people:
            result.append({"type": "people", "data": fav.people.serialize()})
        elif fav.planet:
            result.append({"type": "planet", "data": fav.planet.serialize()})
    return jsonify(result), 200

@app.route('/favorite', methods=['POST'])
def add_favorite():
    user = User.query.get(1)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    data = request.get_json()
    people_id = data.get("people_id")
    planet_id = data.get("planet_id")
    if not people_id and not planet_id:
        return jsonify({"msg": "Debe enviar people_id o planet_id"}), 400

    if people_id:
        if Favorite.query.filter_by(user_id=user.id, people_id=people_id).first():
            return jsonify({"msg": "Person already in favorites"}), 400
        favorite = Favorite(user=user, people_id=people_id)
    else:
        if Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first():
            return jsonify({"msg": "Planet already in favorites"}), 400
        favorite = Favorite(user=user, planet_id=planet_id)

    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite', methods=['DELETE'])
def delete_favorite():
    user = User.query.get(1)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    data = request.get_json()
    people_id = data.get("people_id")
    planet_id = data.get("planet_id")
    if not people_id and not planet_id:
        return jsonify({"msg": "Debe enviar people_id o planet_id"}), 400

    if people_id:
        favorite = Favorite.query.filter_by(user_id=user.id, people_id=people_id).first()
    else:
        favorite = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()

    if not favorite:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorito eliminado"}), 200








# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
