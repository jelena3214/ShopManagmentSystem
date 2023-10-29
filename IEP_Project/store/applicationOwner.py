from functools import wraps
import json
import requests
import csv
from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from configuration import Configuration
from models import *

# If we have to provide this services just for producers
def require_producer_token(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or "role" not in claims or claims["role"] != "Vlasnik":
            return jsonify(msg="Missing Authorization Header"), 401
        return fn(*args, **kwargs)
    return wrapper

application = Flask(__name__)
application.config.from_object(Configuration)
migrate = Migrate(application, database)

@application.route("/", methods = ["GET"])
def hello_world():
    return "<h1>Hello world!</h1>"

database.init_app(application)

jwt = JWTManager (application)

class ItemStub():
    def __init__(self, name, price, categories) -> None:
        self.name = name
        self.price = price
        self.categories = categories

# category1|category2...;name;price
@application.route("/update", methods = ["POST"])
@require_producer_token
def update():
    if 'file' not in request.files:
        return jsonify(message = "Field file is missing."), 400
    
    csv_data = request.files['file'].read().decode('utf-8')
    reader = csv.reader(csv_data.splitlines(), delimiter='\n')

    new_items = []

    for index, row in enumerate(reader):
        data = row[0].split(",")
        if len(data) < 3:
            return jsonify(message = "Incorrect number of values on line " + str(index) + "."), 400
        try:
            price = float(data[2])
        except Exception:
            return jsonify(message = "Incorrect price on line " + str(index) + "."), 400
        
        if price <= 0:
            return jsonify(message = "Incorrect price on line " + str(index) + "."), 400
        item = Item.query.filter(Item.name == data[1]).first()
        if item:
            return jsonify(message = f"Product {data[1]} already exists."), 400
        new_items.append(ItemStub(data[1], float(data[2]), data[0].split("|")))

    for item in new_items:
        new_item = Item(name = item.name, price = item.price)
        database.session.add(new_item)
        database.session.commit()
        for cat in item.categories:
            category = Category.query.filter(Category.name == cat).first()
            if not category:
                category = Category(name = cat)
                database.session.add(category)
                database.session.commit()
            category_item= ItemCategory(item_id = new_item.id, category_id = category.id)
            database.session.add(category_item)
            database.session.commit()

    return make_response('', 200)


@application.route("/product_statistics", methods = ["GET"])
@require_producer_token
def product_statistics():
    json_result = requests.get('http://sparkapp:5007/products').json()
    input_list = json.loads(json_result)

    output_data = []
    for item in input_list:
        if item['done'] > 0 or item['waiting'] > 0:
            output_data.append({
                "name": item['name'],
                "sold": item['done'],
                "waiting": item['waiting']
            })
    
    result = {
        "statistics": output_data
    }

    result_json = json.dumps(result)

    return make_response(result_json, 200)

@application.route("/category_statistics", methods = ["GET"])
@require_producer_token
def category_statistics():
    json_result = requests.get('http://sparkapp:5007/categories').json()
    categories = json.loads(json_result)

    result = {
        "statistics": [item['name'] for item in categories]
    }

    result_json = json.dumps(result)

    return make_response(result_json, 200)



if (__name__ == "__main__"):
    application.run(debug = True, host = "0.0.0.0", port=5004)