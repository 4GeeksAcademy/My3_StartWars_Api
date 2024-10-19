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
from models import db, User, Planet, Vehicle, Character, FavoriteCharacter, FavoriteVehicle, FavoritePlanet
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

@app.route('/people', methods=['GET'])
def get_all_characters():
    all_characters = Character.query.all()
    if not len(all_characters) > 0:
        return jsonify({"error": "Characters not found"}), 404
    serialized_characters = [character.serialize() for character in all_characters]
    return jsonify(serialized_characters), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/planet', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    if not len(all_planets) > 0:
        return jsonify({"error": "Planets not found"}), 404
    serialized_planets = [planet.serialize() for planet in all_planets]
    return jsonify(serialized_planets), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/vehicle', methods=['GET'])
def get_all_vehicles():
    all_vehicles = Vehicle.query.all()
    if not len(all_vehicles) > 0:
        return jsonify({"error": "Vehicles not found"}), 404
    serialized_vehicles = [vehicle.serialize() for vehicle in all_vehicles]
    return jsonify(serialized_vehicles), 200

@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_one_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    return jsonify(vehicle.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    if not len(all_users) > 0:
        return jsonify({"error": "Users not found"}), 404
    serialized_users = [user.serialize() for user in all_users]
    return jsonify(serialized_users), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_one_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize_favorites()), 200

@app.route('/favorite/user/<int:user_id>/people/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    is_favorite = FavoriteCharacter.query.filter_by(user_id=user_id, character_id=character_id).first()
    if is_favorite:
        return jsonify({"error": "Favorite already exists"}), 409
    new_favorite = FavoriteCharacter(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify("El character favorito se agrego exitosamente"), 201

@app.route('/favorite/user/<int:user_id>/people/<int:character_id>', methods=['DELETE'])
def del_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    favorite = FavoriteCharacter.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify("El character se elimino de favorito se agrego exitosamente"), 201

@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    is_favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if is_favorite:
        return jsonify({"error": "Favorite already exists"}), 409
    new_favorite = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify("El planeta favorito se agrego exitosamente"), 201

@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def del_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify("El planeta se elimino de favorito se agrego exitosamente"), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)