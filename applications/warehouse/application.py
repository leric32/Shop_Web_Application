from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
from configuration import Configuration
from models import database
from redis import Redis
import io
import csv
import json
from functools import wraps
from flask import Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


def role_check(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["roles"] is None:
                return jsonify(msg='Missing Authorization Header'), 401
            if ("roles" in claims) and (role in claims["roles"]):
                return function(*arguments, **keyword_arguments)
            else:
                return jsonify(msg='Missing Authorization Header'), 401

        return decorator

    return inner_role


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def deleteFromRedis(ind):
    for i in range(ind):
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpop(name=Configuration.REDIS_THREADS_LIST)


@application.route("/update", methods=["POST"])
@role_check(role="warehouse")
def update():
    file = request.files.get('file')

    file_empty = 0 if file else 1

    if file_empty:
        return jsonify(message="Field file is missing."), 400

    content = request.files["file"].stream.read().decode('utf-8')
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    ind = 0
    list = []

    for row in reader:
        print(row)
        if len(row) != 4:
            # deleteFromRedis(ind)
            return jsonify(message="Incorrect number of values on line " + str(ind) + "."), 400
        if not row[2].isdigit() or int(row[2]) <= 0:
            # deleteFromRedis(ind)
            return jsonify(message="Incorrect quantity on line " + str(ind) + "."), 400
        if not isfloat(row[3]) or float(row[3]) <= 0:
            # deleteFromRedis(ind)
            return jsonify(message="Incorrect price on line " + str(ind) + "."), 400
        list.append(row)
        ind += 1

    for row in list:
        print(row)
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_THREADS_LIST,
                        json.dumps({"category": row[0], "name": row[1], "quantity": row[2], "price": row[3]}))
            # redis.publish(Configuration.REDIS_SUBSCRIBE_CHANNEL, "poruka")

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
