from flask import Flask, jsonify, make_response, request
from configuration import Configuration
from models import *
from functions import *

from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_jwt_extended import create_access_token

#blacklist = set()

application = Flask ( __name__ )
application.config.from_object (Configuration)

@application.route ( "/", methods = ["GET"] )
def hello_world ( ):
    return "<h1>Hello world!</h1>"

database.init_app (application)

@application.route ( "/register_customer", methods = ["POST"] )
def register_customer():
    required_fields = ['forename', 'surname', 'email', 'password']
    missing_fields = [field for field in required_fields if field not in request.json or len(request.json[field]) == 0]

    # Returns first field that does not meet the requirements
    if missing_fields:
        return jsonify(message="Field {} is missing.".format(missing_fields[0])), 400
    
    # Checks if email is valid
    if not is_valid_email(request.json['email']) or len(request.json['email']) > 256:
        return jsonify(message="Invalid email."), 400
    
    # Checks if password length is correct
    if len(request.json['password']) < 8 or len(request.json['password']) > 256:
        return jsonify(message="Invalid password."), 400
    
    user = User.query.filter_by(email=request.json['email']).first()
    if user:
        return jsonify(message="Email already exists."), 400
    
    if len(request.json['forename']) > 256:
        return jsonify(message="Invalid forename length."), 400

    new_user = User (
        first_name = request.json["forename"],
        last_name = request.json["surname"],
        email = request.json["email"],
        password= request.json["password"]
    )

    new_user.role_id = 1

    database.session.add(new_user)
    database.session.commit()

    return make_response('', 200)


@application.route ( "/register_courier", methods = ["POST"] )
def register_courier():
    required_fields = ['forename', 'surname', 'email', 'password']
    missing_fields = [field for field in required_fields if field not in request.json or len(request.json[field]) == 0]

    # Returns first field that does not meet the requirements
    if missing_fields:
        return jsonify(message="Field {} is missing.".format(missing_fields[0])), 400
    
    # Checks if email is valid
    if not is_valid_email(request.json['email']) or len(request.json['email']) > 256:
        return jsonify(message="Invalid email."), 400
    
    # Checks if password length is correct
    if len(request.json['password']) < 8 or len(request.json['password']) > 256:
        return jsonify(message="Invalid password."), 400
    
    user = User.query.filter_by(email=request.json['email']).first()
    if user:
        return jsonify(message="Email already exists."), 400
    
    if len(request.json['forename']) > 256:
        return jsonify(message="Invalid forename length."), 400

    new_user = User (
        first_name = request.json["forename"],
        last_name = request.json["surname"],
        email = request.json["email"],
        password= request.json["password"]
    )

    new_user.role_id = 3

    database.session.add(new_user)
    database.session.commit()

    return make_response('', 200)

jwt = JWTManager ( application )

@application.route("/login", methods = ["POST"])
def login():
    required_fields = ['email', 'password']
    missing_fields = [field for field in required_fields if field not in request.json or len(request.json[field]) == 0]

    # Returns first field that does not meet the requirements
    if missing_fields:
        return jsonify(message="Field {} is missing.".format(missing_fields[0])), 400
    
    # Checks if email is valid
    if not is_valid_email(request.json['email']) or len(request.json['email']) > 256:
        return jsonify(message="Invalid email."), 400

    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter(User.email == email, User.password == password).first()

    if not user:
        return jsonify(message="Invalid credentials."), 400
    
    if len(request.json['password']) > 256:
        return jsonify(message="Invalid password length."), 400

    claims = {
        "forename": user.first_name,
        "surname": user.last_name,
        "role": user.role.name
    }

    access_token  = create_access_token(identity = user.email, additional_claims = claims)

    return jsonify(accessToken = access_token), 200

@application.route("/delete", methods = ["POST"])
@jwt_required()
def delete_user():
    identity = get_jwt_identity()
    user = User.query.filter(User.email == identity).first()

    if not user:
        return jsonify(message = 'Unknown user.'), 400
    
    database.session.delete(user)
    database.session.commit()

    #TODO What do to with jwt tokens?
    #jti = get_jwt()['jti']
    #blacklist.add(jti)

    return make_response('', 200)



if ( __name__ == "__main__" ):
    application.run(debug = True, host = "0.0.0.0", port = 5002)