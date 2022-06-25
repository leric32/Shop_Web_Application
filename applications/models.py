from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    categories = database.Column(database.String(256), nullable=False)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    sold = database.Column(database.Integer, nullable=False)
    waiting = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return self.name

    def as_dict(self):
        return {
            "id": self.id,
            "categories": self.categories,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "sold": self.sold,
            "waiting": self.waiting
        }


class Request(database.Model):
    __tablename__ = "requests"
    id = database.Column(database.Integer, primary_key=True)
    idP = database.Column(database.Integer, nullable=False)
    idO = database.Column(database.Integer, nullable=False)
    priceOfProduct = database.Column(database.Float, nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    received = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return str(self.id)

    def as_dict(self):
        return {
            "id": self.id,
            "idP": self.idP,
            "idO": self.idO,
            "priceOfProduct": self.priceOfProduct,
            "requested": self.requested,
            "received": self.received
        }


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    status = database.Column(database.String(256), nullable=False)
    date = database.Column(database.DateTime, nullable=False)
    price = database.Column(database.Float, nullable=False)
    idC = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return self.status

    def as_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "date": self.date,
            "price": self.price,
            "idC": self.idC
        }
