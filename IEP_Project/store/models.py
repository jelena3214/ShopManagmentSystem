from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate

database = SQLAlchemy()
migrate = Migrate()

class Item(database.Model):
    __tablename__ = 'item'
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), unique=True)
    price = database.Column(database.Double)

    # all, delete-orphan deletes ItemCategory rows associated with this item when we delete it
    categories = database.relationship('ItemCategory', back_populates='item', cascade='all, delete-orphan')
    orders = database.relationship('OrderItem', back_populates='item')

class Category(database.Model):
    __tablename__ = 'category'
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256))

    items = database.relationship('ItemCategory', back_populates='category', cascade='all, delete-orphan')

class ItemCategory(database.Model):
    __tablename__ = 'item_category'
    item_id = database.Column(database.Integer, database.ForeignKey('item.id'), primary_key=True)
    category_id = database.Column(database.Integer, database.ForeignKey('category.id'), primary_key=True)

    item = database.relationship('Item', back_populates='categories')
    category = database.relationship('Category', back_populates='items')

class Order(database.Model):
    __tablename__ = 'order'
    id = database.Column(database.Integer, primary_key = True)
    email = database.Column(database.String(256))
    total_price = database.Column(database.Double)
    status = database.Column(database.String(256))
    date = database.Column(database.DateTime)
    contract_hash = database.Column(database.String(256), default = "")

    items = database.relationship('OrderItem', back_populates='order')

class OrderItem(database.Model):
    __tablename__ = 'order_item'
    order_id = database.Column(database.Integer, database.ForeignKey('order.id'), primary_key=True)
    item_id = database.Column(database.Integer, database.ForeignKey('item.id'), primary_key=True)
    quantity = database.Column(database.Integer, default = 0)

    item = database.relationship('Item', back_populates='orders')
    order = database.relationship('Order', back_populates='items')