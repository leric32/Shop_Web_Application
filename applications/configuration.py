import os

databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shop"
    REDIS_HOST = os.getenv('REDIS_HOST', default="")
    REDIS_THREADS_LIST = "products"
    REDIS_SUBSCRIBE_CHANNEL = "productsChannel"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_DECODE_LEEWAY = 300
