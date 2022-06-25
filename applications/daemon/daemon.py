import json
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
from configuration import Configuration
from redis import Redis
import threading
from models import database, Product, Request, Order

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)


def daemon():
    while True:
        with application.app_context() as context:
            with Redis(Configuration.REDIS_HOST) as redis:
                try:
                    # sub = redis.pubsub()
                    # sub.subscribe(Configuration.REDIS_SUBSCRIBE_CHANNEL)
                    # for item in sub.listen():
                    print("primio poruku")
                    bytes = redis.blpop(Configuration.REDIS_THREADS_LIST)
                    print(json.loads(bytes[1].decode("utf-8"))["name"])
                    prod = json.loads(bytes[1].decode("utf-8"))
                    print(1)
                    p = Product.query.filter(Product.name == prod["name"]).first()
                    print(2)

                    if not p:
                        print("nema ga u bazi")
                        pr = Product(categories=prod["category"], name=prod["name"], quantity=prod["quantity"],
                                     price=prod["price"], sold=0, waiting=0)
                        database.session.add(pr)
                        database.session.commit()
                    else:
                        print("ima ga u bazi")
                        print(p.as_dict())
                        list1 = prod["category"].split("|")
                        list2 = p.as_dict()["categories"].split("|")
                        list1.sort()
                        list2.sort()
                        print(list1)
                        print(list2)
                        if list1 == list2 and prod["name"] == p.as_dict()["name"]:
                            print("UBACUJEMO")
                            print(prod)
                            dq = int(prod["quantity"])
                            dp = float(prod["price"])
                            cq = int(p.as_dict()["quantity"])
                            cp = float(p.as_dict()["price"])
                            np = (cq*cp + dq*dp)/(cq+dq)
                            nq = cq + dq
                            unique_id = int(p.as_dict()["id"])
                            database.session.execute(
                                'UPDATE products SET price =:price, quantity =:quantity WHERE id =:unique_id',
                                {"price": np, "quantity": nq, "unique_id": unique_id}
                            )
                            waiting = p.as_dict()["waiting"]
                            s = p.as_dict()["sold"]
                            if waiting > 0:
                                tmp = nq
                                idP = int(p.as_dict()["id"])
                                w = 0
                                n = 0
                                if nq - waiting >= 0:
                                    n = nq - waiting
                                    w = 0
                                    s += waiting
                                else:
                                    w = waiting - nq
                                    s += nq
                                    n = 0

                                database.session.execute(
                                    'UPDATE products SET waiting =:waiting, quantity =:quantity, sold =:sold WHERE id =:unique_id',
                                    {"waiting": w, "quantity": n, "sold": s,  "unique_id": idP}
                                )

                                req = Request.query.filter(Request.idP == idP).all()
                                for r in req:
                                    if int(r.as_dict()["requested"]) > int(r.as_dict()["received"]):
                                        idR = int(r.as_dict()["id"])
                                        req = int(r.as_dict()["requested"])
                                        rec = int(r.as_dict()["received"])

                                        dif = -1

                                        if rec + tmp >= req:
                                            tmp -= req - rec
                                            rec = req
                                        else:
                                            rec += tmp
                                            tmp = 0

                                        database.session.execute(
                                            'UPDATE requests SET received =:received WHERE id =:unique_id',
                                            {"received": rec, "unique_id": idR}
                                        )
                                        database.session.commit()

                                orders = Order.query.all()
                                for order in orders:
                                    status = order.as_dict()["status"]

                                    if status == "PENDING":
                                        ind = True
                                        idO = int(order.as_dict()["id"])

                                        reqs = Request.query.filter(Request.idO == idO).all()
                                        for r in reqs:
                                            req = int(r.as_dict()["requested"])
                                            rec = int(r.as_dict()["received"])
                                            if req != rec:
                                                ind = False

                                        if ind:
                                            database.session.execute(
                                                'UPDATE orders SET status =:status WHERE id =:unique_id',
                                                {"status": "COMPLETE", "unique_id": idO}
                                            )

                            database.session.commit()

                except Exception as e:
                    print(e)


if __name__ == '__main__':
    daemon()
