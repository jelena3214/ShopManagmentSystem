from functools import wraps
import json
from eth_account import Account
from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from configuration import Configuration
from models import *
import os
import datetime
from web3 import Web3
from eth_utils import is_address
import math

GANACHE_URL = os.environ["GANACHE_URL"]
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))


application = Flask(__name__)
application.config.from_object(Configuration)
migrate = Migrate(application, database)

@application.route("/", methods = ["GET"])
def hello_world():
    return "<h1>Hello world!</h1>"

database.init_app(application)

jwt = JWTManager (application)

# If we have to provide this services just for buyers
def require_buyer_token(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or "role" not in claims or claims["role"] != "Kupac":
            return jsonify(msg="Missing Authorization Header"), 401
        return fn(*args, **kwargs)
    return wrapper


@application.route("/search", methods = ["GET"])
@require_buyer_token
def search():
    category_str = request.args.get('category', default=None)
    item_name = request.args.get('name', default=None)

    query = Category.query.join(ItemCategory).join(Item)

    if category_str:
        query = query.filter(Category.name.like('%{}%'.format(category_str)))

    if item_name:
        query = query.filter(Item.name.like('%{}%'.format(item_name)))

    categories = query.distinct().all()
    category_ids = [category.id for category in categories]

    queryItem = Item.query.join(ItemCategory)

    if item_name:
        queryItem = queryItem.filter(Item.name.like('%{}%'.format(item_name)))

    queryItem = queryItem.filter(ItemCategory.category_id.in_(category_ids))

    products = queryItem.distinct().all()


    product_data = []
    for product in products:
        product_categories = [item_category.category.name for item_category in product.categories]
        product_info = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "categories": product_categories
        }
        product_data.append(product_info)

    response = {
        "categories": [category.name for category in categories],
        "products": product_data
    }
    return jsonify(response), 200


def read_file(path):
    with open(path, 'r') as file:
        return file.read()

with open('keys.json', 'r') as file:
    private_key = Account.decrypt(file.read(), 'asdasdasd').hex()

owner_account = Account.from_key(private_key)


@application.route("/order", methods = ["POST"])
@require_buyer_token
def order():
    if 'requests' not in request.json:
        return jsonify(message = 'Field requests is missing.'), 400
    
    data = request.json['requests']
    total_price = 0
    for index, item in enumerate(data):
        try:
            id = item['id']
        except Exception:
            return jsonify(message = f'Product id is missing for request number {index}.'), 400
        
        try:
            quantity = item['quantity']
        except Exception:
            return jsonify(message = f'Product quantity is missing for request number {index}.'), 400
        
        try:
            int_id = int(id)
        except:
            return jsonify(message = f'Invalid product id for request number {index}.'), 400

        if int_id <= 0:
            return jsonify(message = f'Invalid product id for request number {index}.'), 400
        
        try:
            int_quantity = int(quantity)
        except:
            return jsonify(message = f'Invalid product quantity for request number {index}.'), 400

        if int_quantity <= 0:
            return jsonify(message = f'Invalid product quantity for request number {index}.'), 400
        
        product = Item.query.filter(Item.id == int_id).first()

        if not product:
            return jsonify(message = f'Invalid product for request number {index}.'), 400
        
        total_price += product.price*int_quantity

    identity = get_jwt_identity()

    if 'address' not in request.json or len(request.json['address']) == 0:
        return jsonify(message = 'Field address is missing.'), 400
    
    if not is_address(request.json['address']):
        return jsonify(message = 'Invalid address.'), 400
    

    bytecode = read_file('../../../sources/DeliveryContract.bin')
    abi = read_file('../../../sources/DeliveryContract.abi')
    wei_amount = math.ceil(total_price)
    consumer_address = request.json['address']
    
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    constructor_arguments = (Web3.to_checksum_address(consumer_address), owner_account.address, wei_amount)
    transaction_hash = contract.constructor(*constructor_arguments).build_transaction({
        'from': owner_account.address,
        'gasPrice': 2100000000,
        'nonce': w3.eth.get_transaction_count(owner_account.address)
    })

    signed_transaction1 = w3.eth.account.sign_transaction(transaction_hash, private_key=owner_account.key.hex())

    # Signing the transaction
    tx_hash1 = w3.eth.send_raw_transaction(signed_transaction1.rawTransaction)

    tx_receipt1 = w3.eth.wait_for_transaction_receipt(tx_hash1)

    new_order = Order(status = 'CREATED', date = datetime.datetime.now(), total_price = total_price, email = identity, contract_hash = tx_receipt1.contractAddress)
    database.session.add(new_order)
    database.session.commit()

    for item in data:
        product = Item.query.filter(Item.id == int(item['id'])).first()
        new_order_item = OrderItem(order_id = new_order.id, item_id = product.id, quantity = int(item['quantity']))
        database.session.add(new_order_item)
        database.session.commit()

    return jsonify(id = int(new_order.id)), 200


@application.route("/status", methods = ["GET"])
@require_buyer_token
def status():
    identity = get_jwt_identity()
    orders = Order.query.filter(Order.email == identity).all()

    order_data = []
    for order in orders:
        order_items = OrderItem.query.filter(OrderItem.order_id == order.id).all()
        products = []
        for oritem in order_items:
            item = Item.query.filter(Item.id == oritem.item_id).first()
            product_categories = [item_category.category.name for item_category in item.categories]
            product_info = {
                "categories": product_categories,
                "name": item.name,
                "price": item.price,
                "quantity": oritem.quantity
            }
            products.append(product_info)
        order_info = {
            "products" : products,
            "price" : order.total_price,
            "status" : order.status,
            "timestamp": order.date.isoformat() + "Z"
        }
        order_data.append(order_info)
    response = {
        "orders": order_data
    }
    return jsonify(response), 200

@application.route("/delivered", methods = ["POST"])
@require_buyer_token
def delivered():
    if 'id' not in request.json:
        return jsonify(message = 'Missing order id.'), 400
    try:
        id = int(request.json['id'])
    except Exception:
        return jsonify(message = 'Invalid order id.'), 400
    order = Order.query.filter(Order.id == id).first()

    if id <= 0 or not order or order.status != "PENDING":
        return jsonify(message = 'Invalid order id.'), 400
    
    if 'keys' not in request.json or len(request.json['keys']) == 0:
        return jsonify(message = 'Missing keys.'), 400
    
    if 'passphrase' not in request.json or len(request.json['passphrase']) == 0:
        return jsonify(message = 'Missing passphrase.'), 400
    
    #Because one test doesn't send good json
    s = request.json['keys'].replace("\'", "\"")
    keys = json.loads(s)
    try:
        address = Web3.to_checksum_address('0x' + keys['address'])
        private_key = Account.decrypt(keys, request.json['passphrase']).hex()
    except Exception as e:
        return jsonify(message = 'Invalid credentials.'), 400
    
    abi = read_file('../../../sources/DeliveryContract.abi')
    contract = w3.eth.contract(address=order.contract_hash, abi=abi)

    try:
        transaction = contract.functions.confirmDelivery().build_transaction({
            'from': address,
            'gasPrice': 2100,
            'nonce': w3.eth.get_transaction_count(address)
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print('Transakcija uspešno potvrđena', flush = True)
        print('Hash transakcije:', receipt.transactionHash.hex(), flush = True)
    except Exception as e:
        error_message = str(e)
        # Determine which require statement caused the error
        if "Only the right customer can confirm delivery" in error_message:
            return jsonify(message = 'Invalid customer account.'), 400
        elif "Not paid" in error_message:
            return jsonify(message = 'Transfer not complete.'), 400
        elif "Courier is not assigned" in error_message:
            return jsonify(message = 'Delivery not complete.'), 400
        else: return jsonify(message = error_message), 400

    order.status = 'COMPLETE'
    database.session.add(order)
    database.session.commit()

    return make_response("", 200)


@application.route("/pay", methods = ['POST'])
@require_buyer_token
def pay():
    if 'id' not in request.json:
        return jsonify(message = 'Missing order id.'), 400
    try:
        id = int(request.json['id'])
    except Exception:
        return jsonify(message = 'Invalid order id.'), 400

    order = Order.query.filter(Order.id == id).first()

    if id <= 0 or not order:
        return jsonify(message = 'Invalid order id.'), 400
    
    if 'keys' not in request.json or len(request.json['keys']) == 0:
        return jsonify(message = 'Missing keys.'), 400
    
    if 'passphrase' not in request.json or len(request.json['passphrase']) == 0:
        return jsonify(message = "Missing passphrase."), 400
    

    s = request.json['keys'].replace("\'", "\"")
    keys = json.loads(s)
    try:
        address = Web3.to_checksum_address('0x' + keys['address'])
        private_key = Account.decrypt(keys, request.json['passphrase']).hex()
    except Exception as e:
        return jsonify(message = 'Invalid credentials.'), 400
    
    acc = Account.from_key(private_key)

    # Get the balance of the account in wei
    balance = w3.eth.get_balance(address)

    order = Order.query.filter(Order.id == id).first()

    abi = read_file('../../../sources/DeliveryContract.abi')
    contract = w3.eth.contract(address=order.contract_hash, abi=abi)

    total_price_wei = math.ceil(order.total_price)
    if  total_price_wei > balance:
        return jsonify(message = "Insufficient funds."), 400
    
    try:
        transaction_hash = contract.functions.pay(address).build_transaction({
            'from': acc.address,
            'value': total_price_wei,
            'gasPrice': 2100,
            'nonce': w3.eth.get_transaction_count(acc.address)
        })

        signed_transaction1 = w3.eth.account.sign_transaction(transaction_hash, private_key=acc.key.hex())

        tx_hash1 = w3.eth.send_raw_transaction(signed_transaction1.rawTransaction)

        tx_receipt1 = w3.eth.wait_for_transaction_receipt(tx_hash1)

        print('Transakcija uspešno potvrđena', flush = True)
        print('Hash transakcije:', tx_receipt1.transactionHash.hex(), flush = True)
    
    except Exception as e:
        error_message = str(e)
        # Determine which require statement caused the error
        if "Already paid" in error_message:
            return jsonify(message = 'Transfer already complete.'), 400
        else: return jsonify(message = error_message), 400
        
    print(contract.functions.getBalance().call(), flush=True)

    return make_response("", 200)


if (__name__ == "__main__"):
    application.run(debug = True, host = "0.0.0.0", port=5005)
