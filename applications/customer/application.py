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
from models import Product, Order, Request
import datetime

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


def checkContainsInProduct(c, name):
    products = Product.query.all()

    for product in products:
        if c in product.as_dict()["categories"] and name in product.as_dict()["name"]:
            return True
    return False


@application.route("/search", methods=["GET"])
@role_check(role="customer")
def search():
    name = str(request.args["name"]) if request.args.get("name") is not None else ""
    category = str(request.args["category"]) if request.args.get("category") is not None else ""
    categories_2 = []
    products_2 = []

    print(name)
    print(category)

    products = Product.query.all()

    for product in products:
        cat = product.as_dict()["categories"].split("|")
        print(cat)
        for c in cat:
            if c not in categories_2 and category in c and checkContainsInProduct(c, name):
                categories_2.append(c)

    print(categories_2)

    products = Product.query.all()

    for product in products:
        prod = product.as_dict()["name"]
        print(prod)
        if name in product.as_dict()["name"] and category in product.as_dict()["categories"]:
            products_2.append({
                "categories": product.as_dict()["categories"].split("|"),
                "id": int(product.as_dict()["id"]),
                "name": product.as_dict()["name"],
                "price": float(product.as_dict()["price"]),
                "quantity": int(product.as_dict()["quantity"])
            })

    return jsonify(categories=categories_2, products=products_2), 200


@application.route("/order", methods=["POST"])
@role_check(role="customer")
def order():
    requests = request.json.get("requests", "")

    requests_empty = True if not requests else False

    if requests_empty:
        return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    ind = 0

    for r in requests:
        id = r.get("id")
        if not id:
            return jsonify(message="Product id is missing for request number " + str(ind) + "."), 400
        elif not str(id).isdigit() or int(id) <= 0:
            return jsonify(message="Invalid product id for request number " + str(ind) + "."), 400

        quan = r.get("quantity")
        if not quan:
            return jsonify(message="Product quantity is missing for request number " + str(ind) + "."), 400
        elif not str(quan).isdigit() or int(id) <= 0:
            return jsonify(message="Invalid product quantity for request number " + str(ind) + "."), 400

        p = Product.query.filter(Product.id == id).first()

        if not p:
            return jsonify(message="Invalid product for request number " + str(ind) + "."), 400

        ind += 1

    suma = 0.0
    completed = True
    verify_jwt_in_request()
    idC = get_jwt()["id"]

    ord = Order(status="COMPLETED", date=datetime.datetime.now().isoformat(), idC=idC, price=suma)
    database.session.add(ord)

    database.session.flush()
    print(ord.id)
    idO = ord.id
    #database.session.commit()

    for r in requests:
        idP = r.get("id")
        quan = r.get("quantity")
        print("idP" + str(idP) + "idC" + str(idC) + "quantity" + str(quan))

        prod2 = Product.query.filter(Product.id == idP).first()
        prod = prod2.as_dict()
        pq = prod["quantity"]
        ps = prod["sold"]
        pw = prod["waiting"]
        pric = prod["price"]

        if pq >= quan:
            pq -= quan
            ps += quan
            suma += quan * pric
            database.session.execute(
                'UPDATE products SET sold =:sold, quantity =:quantity WHERE id =:unique_id',
                {"sold": ps, "quantity": pq, "unique_id": idP}
            )
            #database.session.commit()
            req = Request(idP=idP, idO=idO, priceOfProduct=pric, requested=quan, received=quan)
            database.session.add(req)
            #database.session.commit()

        else:
            completed = False
            tmp = 0
            if pq == 0:
                tmp = 0
            else:
                tmp = pq
                pq = 0
                ps += tmp
            suma += quan * pric
            pw += quan - tmp
            database.session.execute(
                'UPDATE products SET sold =:sold, quantity =:quantity, waiting =:waiting WHERE id =:unique_id',
                {"sold": ps, "quantity": pq, "waiting": pw, "unique_id": idP}
            )
            req = Request(idP=idP, idO=idO, priceOfProduct=pric, requested=quan, received=tmp)
            database.session.add(req)


    print("CENA = " + str(suma))
    strC = "COMPLETE" if completed else "PENDING"
    #orderC = Order(id=idO, status=strC, date=datetime.datetime.now().isoformat(), price=suma, idC=idC)
    database.session.execute(
        'UPDATE orders SET price =:price, status =:status WHERE id =:unique_id',
        {"price": suma, "status": strC, "unique_id": idO}
    )
    #database.session.add(orderC)
    database.session.commit()

    return jsonify(id=idO), 200


@application.route("/status", methods=["GET"])
@role_check(role="customer")
def status():
    verify_jwt_in_request()
    idC = get_jwt()["id"]

    orders = Order.query.filter(Order.idC == idC).all()

    order_2 = []

    for order1 in orders:
        idO = order1.as_dict()["id"]
        reqs = Request.query.filter(Request.idO == idO).all()

        products_2 = []

        for req in reqs:
            idP = req.as_dict()["idP"]
            product = Product.query.filter(Product.id == idP).first()
            products_2.append({
                "categories": product.as_dict()["categories"].split("|"),
                "name": product.as_dict()["name"],
                "price": float(req.as_dict()["priceOfProduct"]),
                "received": int(req.as_dict()["received"]),
                "requested": int(req.as_dict()["requested"]),
            })

        order_2.append({
            "products": products_2,
            "price": float(order1.as_dict()["price"]),
            "status": order1.as_dict()["status"],
            "timestamp": order1.as_dict()["date"].isoformat()
        })

    return jsonify(orders=order_2), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
