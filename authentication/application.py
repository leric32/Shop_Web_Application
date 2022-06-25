import json

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re
#from applications.admin.adminDecorater import role_check
from functools import wraps
from flask import Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

application = Flask(__name__)
application.config.from_object(Configuration)


def role_check(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            verify_jwt_in_request()
            claims = get_jwt()
            # if claims["roles"] is None:
            #     return jsonify(msg='Missing Authorization Header'), 401
            # if ("roles" in claims) and (role in claims["roles"]):
            #     return function(*arguments, **keyword_arguments)
            # else:
            #     return jsonify(msg='Missing Authorization Header'), 401
            if "roles" in claims and role in claims["roles"]:
                return function(*arguments, **dict(**keyword_arguments))
            else:
                message = jsonify(msg="Missing Authorization Header")
                message.status_code = 401
                return message
        return decorator
    return inner_role


@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", "")

    email_empty = len(email) == 0
    password_empty = len(password) == 0
    forename_empty = len(forename) == 0
    surname_empty = len(surname) == 0
    isCustomer_empty = isCustomer == ""

    if forename_empty:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)
    elif surname_empty:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    elif email_empty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    elif password_empty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)
    elif isCustomer_empty:
        return Response(json.dumps({"message": "Field isCustomer is missing."}), status=400)

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    res1 = True if next((chr for chr in password if chr.isdigit()), None) else False
    res2 = True if next((chr for chr in password if chr.islower()), None) else False
    res3 = True if next((chr for chr in password if chr.isupper()), None) else False

    if len(password) < 8 or not res1 or not res2 or not res3:
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    users = User.query.filter(User.email == email).all()
    print(len(users))

    if len(users) > 0:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    user = User(email=email, password=password, forename=forename, surname=surname, isCustomer=isCustomer)
    database.session.add(user)
    database.session.commit()

    if isCustomer:
        user_role = UserRole(userId=user.id, roleId=2)
        database.session.add(user_role)
        database.session.commit()
    else:
        user_role = UserRole(userId=user.id, roleId=3)
        database.session.add(user_role)
        database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    email_empty = len(email) == 0
    password_empty = len(password) == 0

    if email_empty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    elif password_empty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    roles = [role.name for role in user.roles]

    roles_field = None if len(roles) == 0 else roles

    additional_claims = {
        "id": user.id,
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        "isCustomer": user.isCustomer,
        "roles": roles_field
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid!"


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        "id": refresh_claims["id"],
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "email": refresh_claims["email"],
        "isCustomer": refresh_claims["isCustomer"],
        "roles": refresh_claims["roles"]
    }

    return jsonify({"accessToken": create_access_token(identity=identity, additional_claims=additional_claims)}), 200


@application.route("/delete", methods=["POST"])
@role_check(role="admin")
def delete():
    email = request.json.get("email", "")

    email_empty = len(email) == 0

    if email_empty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify(message="Unknown warehouse."), 400

    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
