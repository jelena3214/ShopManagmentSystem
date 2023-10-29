from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate

database = SQLAlchemy()
migrate = Migrate()


class Role (database.Model):
    __tablename__ = 'role'
    id   = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String (256), nullable = False)
    users = database.relationship ("User", backref = "role")

class User(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256), nullable = False, unique = True)
    password = database.Column(database.String(256), nullable = False)
    first_name = database.Column(database.String(256), nullable = False)
    last_name = database.Column(database.String(256), nullable = False)
    role_id = database.Column(database.Integer, database.ForeignKey('role.id'), nullable=False)

    def __init__ (self, email, password, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
