from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if (not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

    database.init_app(application)

    with application.app_context() as context:
        init()
        migrate(message = "Initial migration")
        upgrade()

        role1 = Role(name = "Kupac")
        role2 = Role(name = "Vlasnik")
        role3 = Role(name = "Kurir")

        database.session.add(role1)
        database.session.add(role2)
        database.session.add(role3)
        database.session.commit()

        user = User (
            first_name = "Scrooge", 
            last_name = "McDuck", 
            email = "onlymoney@gmail.com", 
            password = "evenmoremoney"
        )
        user.role_id = 2

        database.session.add(user)
        database.session.commit()