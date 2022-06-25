
#while True:
x = True

from flask import Flask, Response, jsonify
from configuration import Configuration
from models import database, Product, Order, Request
#from adminDecorater import role_check
from flask_jwt_extended import JWTManager
from functools import wraps
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

@application.route("/productStatistics", methods=["GET"])
@role_check(role="admin")
def product_statistics():
    products_2 = []

    products = Product.query.all()

    for product in products:
        sold = int(product.as_dict()["sold"]) + int(product.as_dict()["waiting"])
        if sold > 0:
            products_2.append({
                "name": product.as_dict()["name"],
                "sold": int(product.as_dict()["sold"]) + int(product.as_dict()["waiting"]),
                "waiting": int(product.as_dict()["waiting"])
            })

    return jsonify(statistics=products_2), 200


@application.route("/categoryStatistics", methods=["GET"])
@role_check(role="admin")
def category_statistics():
    categories_2 = []
    cat = {}
    products = Product.query.all()

    for product in products:
        sold = int(product.as_dict()["sold"]) + int(product.as_dict()["waiting"])
        categories = product.as_dict()["categories"].split("|")

        for category in categories:
            if category in cat.keys():
                cat[category] += sold
            else:
                cat[category] = sold

    sorted_dict = [v[0] for v in sorted(cat.items(), key=lambda kv: (-kv[1], kv[0]))]

    print(sorted_dict)

    # categories_2 = list(sorted_dict.keys())

    return jsonify(statistics=sorted_dict), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
