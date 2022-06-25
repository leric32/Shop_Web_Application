from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User, UserRole
from sqlalchemy_utils import database_exists, create_database
import os
import shutil

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False
if os.path.exists("migrations"):
    shutil.rmtree("migrations")

while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()

            admin_role = Role(name="admin")
            user_role = Role(name="customer")
            user_role2 = Role(name="warehouse")

            database.session.add(admin_role)
            database.session.add(user_role)
            database.session.add(user_role2)
            database.session.commit()

            admin = User(
                forename="admin",
                surname="admin",
                email="admin@admin.com",
                password="1",
                isCustomer=True
            )

            database.session.add(admin)
            database.session.commit()

            user_role = UserRole(
                userId=admin.id,
                roleId=admin_role.id
            )

            database.session.add(user_role)
            database.session.commit()

            done = True
    except Exception:
        pass